# Copyright (c) Polyconseil SAS. All rights reserved.
"""OCPP-JSON serialization, parsing and validation."""
import copy
import dataclasses
from dataclasses import fields
from dataclasses import is_dataclass
import functools
import logging
import sys
import typing

from ocpp_codec import compat
from ocpp_codec import errors
from ocpp_codec import exceptions
from ocpp_codec import structure
from ocpp_codec import types
from ocpp_codec import validators


logger = logging.getLogger(__name__)


def _is_optional(field: dataclasses.Field) -> bool:
    return field.default is None


def _is_undefined(field: dataclasses.Field, value: typing.Any) -> bool:
    # Special case to consider [] as undefined for List types
    return value is None or (_is_list(field.type) and not value)


def required_fields(dataclass_class) -> typing.List[dataclasses.Field]:
    return [field for field in fields(dataclass_class) if not _is_optional(field)]


def _run_validator(field: dataclasses.Field, data: typing.Any, *, parsing: bool) -> typing.Any:
    # Fetch the validator to run
    validator = field.metadata.get('validator', validators.noop)
    if isinstance(validator, validators.BaseEncoder):
        # Pick the right method based on whether we're parsing a message, or serializing a field
        validator = validator.from_json if parsing else validator.to_json

    try:
        validated_data = validator(data)
    except errors.BaseOCPPError as exc:
        # Inject field data in exception, as the validator doesn't know the field's name
        exc.details.setdefault('field', field.name)
        raise exc
    else:
        return validated_data


# Both _is_list and _is_generic use some private API, beware. There exists a third-party library
# https://github.com/ilevkivskyi/typing_inspect to inspect these types, but it uses just as much private API. Something
# will most likely be added to the typing module at some point to handle this kind of manipulation, keep it simple for
# now.

def _is_list(type_):
    return hasattr(type_, '__origin__') and issubclass(type_.__origin__, typing.Sequence)


def _is_generic(type_):
    if (3, 6) <= sys.version_info < (3, 7):
        return isinstance(type_, typing.GenericMeta)
    return isinstance(type_, typing._GenericAlias)


def _unpack_field(field: dataclasses.Field) -> dataclasses.Field:
    """Extract the type contained inside the generic definition.

    Replaces the field's type with the type contained inside its generic type, e.g.: List[int] -> int

    The returned field is a copy of the original, as the original resides in the class definition. Modifying it would be
    destructive.
    """
    new_field = copy.copy(field)
    new_field.type = field.type.__args__[0]
    return new_field


def _extract_base_type(field: dataclasses.Field) -> dataclasses.Field:
    """Extract the real type out of a SimpleType instance.

    The returned field is a copy of the original, as the original resides in the class definition. Modifying it would be
    destructive.

    The SimpleType instance is expected to have only a single field.
    """
    new_field = copy.copy(fields(field.type)[0])
    new_field.name = field.name
    return new_field


#########
# Parsing

def parse_field(field: dataclasses.Field, data: typing.Any) -> typing.Any:
    """Tries to fit a JSON object into a dataclass field.

    Makes sure the data received from the network connection is of the expected type, before validation.

    Args:
        - field: dataclasses.Field, the field to match the data against
        - data: object, any kind of data retrieved from the OCPP-JSON message (string, integer, list, dict, etc.)

    Returns:
        object, a validated piece of data, ran through the field's validator and maybe converted to a more convenient
        type.

    Raises:
        - errors.TypeConstraintViolationError
        - errors.PropertyConstraintViolationError
    """
    # First, make sure we received the type we were expecting. 'isinstance' is supposedly slow, but until we get some
    # metric on performance, use it.
    if not isinstance(data, field.type):
        raise errors.TypeConstraintViolationError(
            f"Value '{data}' is not of type '{field.type.__name__}' (type is '{type(data).__name__}')",
            value=data, field=field.name,
        )

    # Will raise if fails
    return _run_validator(field, data, parsing=True)


def parse_data(dataclass_class, data):
    """Tries to match every elements from a dict into a dataclass' fields.

    The 'data' dict shall at least contain the fields required by the dataclass, or an error will be raised.

    Args:
        - dataclass_class: dataclasses.dataclass, the dataclass to match the data against
        - data: dict, the data to fit into the dataclass, keys must match the dataclass' fields names

    Returns:
        dataclass, an instance of 'dataclass_class' populated with the data found in 'data'

    Raises:
        - errors.ProtocolError
        - errors.TypeConstraintViolationError
        - errors.PropertyConstraintViolationError
    """
    dataclass_fields = fields(dataclass_class)

    if len(data) > len(dataclass_fields):
        logger.warning(
            "Data has more fields than expected. Got: '%s' for message '%s'",
            ', '.join(data.keys()),
            dataclass_class.__name__
                if not hasattr(dataclass_class, '_action_class') else dataclass_class._action_class.__name__,
        )
        raise errors.ProtocolError("Too many arguments provided")

    # Make sure every required fields can be found in data, and are defined
    req_fields = set(required_fields(dataclass_class))
    req_fields_names = {field.name for field in req_fields}
    provided_fields_names = set(data.keys())
    if (
        provided_fields_names & req_fields_names != req_fields_names
        or any(_is_undefined(field, data[field.name]) for field in req_fields)
    ):
        raise errors.ProtocolError(
            f"Missing or undefined/empty required fields",
            required_fields=sorted(req_fields_names), provided_fields=sorted(provided_fields_names),
        )

    # Match every piece of data against the dataclass fields
    validated_data = {}
    for field in dataclass_fields:
        # Skip optional undefined or non-provided fields
        if _is_optional(field) and (field.name not in data or _is_undefined(field, data[field.name])):
            continue

        # Simple types wrap a base Python types, get it. Generics cannot be used with issubclass and would crash, we
        # must be careful
        if not _is_generic(field.type) and issubclass(field.type, types.SimpleType):
            field = _extract_base_type(field)

        data_item = data[field.name]
        if is_dataclass(field.type):
            validated_data[field.name] = parse_data(field.type, data_item)
        elif _is_list(field.type):
            if not isinstance(data_item, list):
                raise errors.TypeConstraintViolationError(
                    f"Field '{field.name}' is not a list (type is {type(data_item).__name__}",
                )
            # Run validator on the list attribute itself, before iterating over its elements
            data_item = _run_validator(field, data_item, parsing=True)
            # Parse the list's elements
            field = _unpack_field(field)
            if is_dataclass(field.type):
                parse_func = functools.partial(parse_data, field.type)
            else:
                parse_func = functools.partial(parse_field, field)
            validated_data[field.name] = [parse_func(element) for element in data_item]
        else:
            validated_data[field.name] = parse_field(field, data_item)

    return dataclass_class(**validated_data)


_MSGTYPEID_TO_DATACLASS = {
    2: structure.Call,
    3: structure.CallResult,
    4: structure.CallError,
}


_DEFAULT_CALLERROR_UNIQUEID = "-1"


def parse(
    raw_data: typing.Any, call_result_action_name: typing.Optional[str] = None, *, protocol: compat.OcppJsonProtocol
) -> structure.OCPPMessage:
    """Fit 'raw_data' based on Python simple types into an 'OCPPMessage' dataclass.

    Args:
        - raw_data: object, Python representation of an OCPPMessage, using only simple types
        - call_result_action_name: str, name of the 'Action' class to use to parse 'CallResult' payloads, only useful
          when parsing such a message, it's ignored otherwise (default: None)
        - protocol: OcppJsonProtocol, which version of the OCPP Json protocol are we using (mostly defines which error
                    codes to use)

    Returns:
        OCPPMessage, a type-checked dataclass instance, using more complex types as defined by the OCPP specification

    Raises:
        - exceptions.OCPPException
    """
    if not isinstance(raw_data, list) or not raw_data:
        logger.warning("Received invalid OCPP '%s'", raw_data)
        raise exceptions.OCPPException(
            compat.get_rpc_framework_error("Message must be a non-empty list", protocol=protocol),
            _DEFAULT_CALLERROR_UNIQUEID,
        )

    msg_type_id = raw_data[0]
    if msg_type_id not in _MSGTYPEID_TO_DATACLASS:
        raise exceptions.OCPPException(
            compat.get_message_type_not_supported_error(f"Message type {msg_type_id} not supported", protocol=protocol),
            _DEFAULT_CALLERROR_UNIQUEID,
        )

    msgtype_dataclass = _MSGTYPEID_TO_DATACLASS[msg_type_id]

    # Convert the list to a dict, using the dataclass fields' names as keys. Items in the list are expected to be in
    # the same order as the dataclass' fields.
    ocpp_dict = {field.name: value for field, value in zip(fields(msgtype_dataclass), raw_data)}

    # as per OCPP 1.6 JSON specification, section 4.2.1, an optional payload can be defined as either the empty
    # object {}, or null. It's easier for us to handle only one, thus convert None to {}.
    if 'payload' in ocpp_dict and ocpp_dict['payload'] is None:
        ocpp_dict['payload'] = {}

    # First, parse the global message structure (Call, CallResult, CallError)
    try:
        ocpp_msg = parse_data(msgtype_dataclass, ocpp_dict)
    except errors.BaseOCPPError as exc:
        raise exceptions.OCPPException(exc, _DEFAULT_CALLERROR_UNIQUEID)

    # Then, extra parsing required for messages with a payload (i.e.: CALL and CALLRESULT)
    if ocpp_msg.messageTypeId in (structure.MessageTypeEnum.CALL, structure.MessageTypeEnum.CALLRESULT):
        if ocpp_msg.messageTypeId is structure.MessageTypeEnum.CALLRESULT and not call_result_action_name:
            raise ValueError("'call_result_action_name' must be provided when decoding a CallResult message")

        is_call = ocpp_msg.messageTypeId is structure.MessageTypeEnum.CALL

        # Fetch the 'Action' dataclass to use for parsing, based either on 'Call.action' or the provided action name
        # when parsing a CallResult based on a previous Call
        action_name = ocpp_msg.action if is_call else call_result_action_name
        implemented_messages = compat.get_implemented_messages(protocol)
        try:
            action_dataclass = implemented_messages[action_name]
        except KeyError:
            exc = errors.NotImplementedError(
                f"Action '{action_name}' is not implemented",
                available_actions=list(implemented_messages.keys()),
            )
            raise exceptions.OCPPException(exc, ocpp_msg.uniqueId)

        if is_call:
            payload_dataclass = compat.get_request_payload_dataclass(action_dataclass)
        else:
            payload_dataclass = compat.get_response_payload_dataclass(action_dataclass)

        try:
            ocpp_msg.payload = parse_data(payload_dataclass, ocpp_msg.payload)
        except errors.BaseOCPPError as exc:
            # Convert to an exception that can be used to form a CallError message
            raise exceptions.OCPPException(exc, ocpp_msg.uniqueId) from exc

    return ocpp_msg


#############
# Serializing

def serialize_field(field: dataclasses.Field, data: typing.Any) -> typing.Any:
    """Serializes a data element against a dataclass field.

    Makes sure the data going out onto the network is of the expected type, after validation.

    Args:
        - field: dataclasses.Field, the field to match the data against
        - data: object, the Python object requiring serialization

    Returns:
        object, a JSON compatible object (string, integer, list, dict, etc.)

    Raises:
        - errors.TypeConstraintViolationError
        - errors.PropertyConstraintViolationError
    """
    # Simple types wrap a base Python types, get it
    if issubclass(field.type, types.SimpleType):
        field = _extract_base_type(field)

    try:
        validated_data = _run_validator(field, data, parsing=False)
    except errors.BaseOCPPError:
        logger.warning("Failed to validate field '%s' with input '%s'", field.name, data)
        raise

    # We only check the field's type after validating, as the validator is very likely to convert the initial type
    # (e.g.: datetime->str or Enum->int).
    if not isinstance(validated_data, field.type):
        raise errors.TypeConstraintViolationError(
            f"Item '{validated_data}' is not of type '{field.type}' (type is '{type(validated_data)}')",
            item=data, field=field.name,
        )

    return validated_data


def serialize_fields(message):
    """Serializes a whole OCPP 'Action.req' or 'Action.conf' based on the dataclass fields.

    Basically serializes every field in order, and return a dict of it all. Can be seen as an equivalent to
    'dataclasses.asdict()', running additional validation based on the message's dataclass fields.

    Recursively serializes nested dataclasses.

    Args:
        - message: 'Action.req' or 'Action.conf', the message to serialize

    Returns:
        dict, an equivalent to the message, based only on JSON compatible types (string, integer, list, dict, etc.)

    Raises:
        - errors.TypeConstraintViolationError
        - errors.PropertyConstraintViolationError
    """
    serialized_dict = {}
    for field in fields(message):
        field_value = getattr(message, field.name)

        if _is_undefined(field, field_value) and _is_optional(field):
            continue
        # This provides a more helpful error than letting the serializing code hit a None field value and yield a
        # validator error. However, this is highly unlikely we'll ever run into this case when using this module
        # properly.
        if _is_undefined(field, field_value) and not _is_optional(field):
            raise errors.ProtocolError(f"Undefined required field '{field.name}'")

        # Must be done first, as issubclass doesn't support being called with typing.List as its first argument (it's
        # not a class)
        if _is_list(field.type):
            # Run validator on the list attribute itself, before iterating over its elements
            field_value = _run_validator(field, field_value, parsing=False)
            # Serialize the list's elements
            field = _unpack_field(field)
            serialize_func = serialize_fields if issubclass(field.type, types.ComplexType) else serialize_field
            serialized_dict[field.name] = [serialize_func(element) for element in field_value]
        elif issubclass(field.type, types.ComplexType):
            serialized_dict[field.name] = serialize_fields(field_value)
        else:
            serialized_dict[field.name] = serialize_field(field, field_value)

    return serialized_dict


def serialize(message: typing.Union[structure.Call, structure.CallResult, structure.CallError]) -> typing.List:
    """Serializes an 'OCPPMessage'.

    Args:
        - message: 'OCPPMessage', the message to serialize

    Returns:
        list, an equivalent to the message, based only on JSON compatible types (string, integer, list, dict, etc.)

    Raises:
        - errors.TypeConstraintViolationError
        - errors.PropertyConstraintViolationError
    """
    # Build the base of the message to serialize. Iterate over the dataclass' fields to get them in order, ignore
    # 'payload' field that needs to be serialized recursively
    ocpp_msg = [
        serialize_field(field, getattr(message, field.name))
        for field in fields(message) if field.name != 'payload'
    ]
    if hasattr(message, 'payload'):
        ocpp_msg.append(serialize_fields(message.payload))

    return ocpp_msg
