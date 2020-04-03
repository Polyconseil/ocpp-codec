# Copyright (c) Polyconseil SAS. All rights reserved.
from dataclasses import fields
import datetime

import pytest
import pytz

from ocpp_codec import compat
from ocpp_codec import errors
from ocpp_codec import exceptions
from ocpp_codec import serializer
from ocpp_codec import structure
from ocpp_codec import types as common_types

from . import messages
from . import types


def test_parse_field():
    validated_field = fields(types.ValidatedType)[0]

    # Check validators are applied
    validated_data = serializer.parse_field(validated_field, 'good_value')
    assert validated_data == 'good_value'

    with pytest.raises(errors.PropertyConstraintViolationError):
        serializer.parse_field(validated_field, 'too_long' * 100)

    with pytest.raises(errors.TypeConstraintViolationError):
        serializer.parse_field(validated_field, 123)

    # Multiple validators are applied in sequence
    positive_float_field = fields(types.SeveralValidatorsType)[0]
    with pytest.raises(errors.PropertyConstraintViolationError):
        serializer.parse_field(positive_float_field, -2.1)
    with pytest.raises(errors.PropertyConstraintViolationError):
        serializer.parse_field(positive_float_field, 2.12)
    validated_data = serializer.parse_field(positive_float_field, 2.1)
    assert validated_data == 2.1

    # Check that a field with an encoder converts the type accordingly
    datetime_field = fields(types.DateTimeType)[0]
    dt = serializer.parse_field(datetime_field, '2019-01-30T12:30:00Z')
    assert isinstance(dt, datetime.datetime) is True

    # Not defining a validator is fine
    simple_field = fields(messages.SimpleAction.req)[0]
    data = 'Anything goooes!' * 100
    validated_data = serializer.parse_field(simple_field, data)
    assert validated_data == data


def test_parse_data():
    # Simple message
    simple_req_msg = serializer.parse_data(messages.SimpleAction.req, {
        'value': 'foo',
        'validatedValue': 'bar',
        'enumValue': 'Foo',
    })
    assert simple_req_msg == messages.SimpleAction.req(
        value='foo',
        validatedValue='bar',
        enumValue=types.FooBarEnum.Foo,
    )
    simple_conf_msg = serializer.parse_data(messages.SimpleAction.conf, {
        'value': 12,
        'datetimeValue': '2019-01-30T12:30Z',
    })
    assert simple_conf_msg == messages.SimpleAction.conf(
        value=12,
        datetimeValue=datetime.datetime(year=2019, month=1, day=30, hour=12, minute=30, tzinfo=pytz.UTC),
    )

    # More complex message, with lists and optional values
    complex_req_msg = serializer.parse_data(messages.ComplexAction.req, {
        'complexValue': {
            'enumValue': 'Foo',
            'validatedValue': 'data',
        },
        'listValue': [
            {
                'datetimeValue': '2019-01-30T12:00Z', 'nestedListValue': [
                    {'value': 'foo'},
                    {'value': 'bar', 'optionalValue': 'Bar'},
                ],
            },
            {'datetimeValue': '2019-01-30T12:30Z', 'nestedListValue': [{'value': 'foobar'}]},
        ],
    })
    assert complex_req_msg == messages.ComplexAction.req(
        complexValue=types.ComplexType(enumValue=types.FooBarEnum.Foo, validatedValue='data'),
        listValue=[
            types.ListElementType(
                datetimeValue=datetime.datetime(year=2019, month=1, day=30, hour=12, minute=0, tzinfo=pytz.UTC),
                nestedListValue=[
                    types.ElementType(value='foo'),
                    types.ElementType(value='bar', optionalValue=types.FooBarEnum.Bar),
                ],
            ),
            types.ListElementType(
                datetimeValue=datetime.datetime(year=2019, month=1, day=30, hour=12, minute=30, tzinfo=pytz.UTC),
                nestedListValue=[
                    types.ElementType(value='foobar'),
                ],
            ),
        ],
        optionalValue=None,
    )

    # Optional list field, provided but empty
    complex_conf_msg = serializer.parse_data(messages.ComplexAction.conf, {'optionalListValue': []})
    assert complex_conf_msg == messages.ComplexAction.conf(optionalListValue=None)

    # Test exceptions are propagated
    with pytest.raises(errors.PropertyConstraintViolationError):
        # 'enumValue' value is not part of FooBarEnum
        serializer.parse_data(
            messages.SimpleAction.req,
            {'value': 'foo', 'validatedValue': 'bar', 'enumValue': 'not_valid'},
        )
    with pytest.raises(errors.TypeConstraintViolationError):
        # 'datetimeValue' isn't of the valid type
        serializer.parse_data(
            messages.SimpleAction.conf,
            {'value': 12, 'datetimeValue': 123},
        )
    with pytest.raises(errors.ProtocolError):
        # 'listValue' is a required non-empty list
        serializer.parse_data(
            messages.ComplexAction.req,
            {'complexValue': {'enumValue': 'Foo', 'validatedValue': 'data'}, 'listValue': []},
        )
    with pytest.raises(errors.PropertyConstraintViolationError):
        # 'listValue' contains at most 4 elements
        serializer.parse_data(
            messages.ComplexAction.req,
            {'complexValue': {'enumValue': 'Foo', 'validatedValue': 'data'}, 'listValue': [
                {'datetimeValue': '2019-01-30T12:30Z', 'nestedListValue': [{'value': 'first'}]},
                {'datetimeValue': '2019-01-30T12:30Z', 'nestedListValue': [{'value': 'second'}]},
                {'datetimeValue': '2019-01-30T12:30Z', 'nestedListValue': [{'value': 'third'}]},
                {'datetimeValue': '2019-01-30T12:30Z', 'nestedListValue': [{'value': 'fourth'}]},
                {'datetimeValue': '2019-01-30T12:30Z', 'nestedListValue': [{'value': 'extra_element'}]},
            ]},
        )

    # Test unexpected arguments
    with pytest.raises(errors.ProtocolError):
        serializer.parse_data(messages.SimpleAction.req, {
            'value': 'data', 'validatedValue': 'data', 'enumValue': 'Foo',
            'extra': 'argument',
        })
    # Test missing required elements
    with pytest.raises(errors.ProtocolError):
        # missing 'enumValue'
        serializer.parse_data(messages.SimpleAction.req, {'value': 'data', 'validatedValue': 'data'})


@pytest.mark.parametrize('protocol,rpcframework_error,msgtype_error', [
    (compat.OcppJsonProtocol.v16, common_types.ErrorCodeEnum.GenericError, common_types.ErrorCodeEnum.GenericError),
    (
        compat.OcppJsonProtocol.v20,
        common_types.ErrorCodeEnum.RpcFrameworkError,
        common_types.ErrorCodeEnum.MessageTypeNotSupported,
    ),
])
def test_parse_structure(protocol, rpcframework_error, msgtype_error):
    # Call
    call_msg = serializer.parse_structure([2, "19223201", "DontCare", {"dont": "care"}], protocol=protocol)
    assert call_msg == structure.Call(
        uniqueId='19223201',
        action='DontCare',
        payload={'dont': 'care'},
    )

    # CallResult
    call_result_msg = serializer.parse_structure([3, "19223201", {"dont": "care"}], protocol=protocol)
    assert call_result_msg == structure.CallResult(uniqueId='19223201', payload={'dont': 'care'})

    # CallError
    call_error_msg = serializer.parse_structure(
        [4, "19223201", "GenericError", "DontCare", {"dont": "care"}],
        protocol=protocol,
    )
    assert call_error_msg == structure.CallError(
        uniqueId='19223201',
        errorCode=common_types.ErrorCodeEnum.GenericError,
        errorDescription='DontCare',
        errorDetails={'dont': 'care'},
    )

    # Empty payload as {} or null is ok
    call_msg = serializer.parse_structure([2, "19223201", "NoPayloadAction", {}], protocol=protocol)
    assert call_msg == structure.Call(
        uniqueId='19223201',
        action='NoPayloadAction',
        payload={},
    )
    call_msg = serializer.parse_structure([2, "19223201", "NoPayloadAction", None], protocol=protocol)
    assert call_msg == structure.Call(
        uniqueId='19223201',
        action='NoPayloadAction',
        payload={},
    )

    # Valid JSON but not OCPP-J
    with pytest.raises(exceptions.OCPPException) as excinfo:
        serializer.parse_structure({"that_is_not": "ocpp-json"}, protocol=protocol)
    assert excinfo.value.as_call_error.errorCode == rpcframework_error
    assert excinfo.value.as_call_error.uniqueId == "-1"
    # Valid OCPP-J but empty list that we cannot guess anything from
    with pytest.raises(exceptions.OCPPException) as excinfo:
        serializer.parse_structure([], protocol=protocol)
    assert excinfo.value.as_call_error.errorCode == rpcframework_error
    assert excinfo.value.as_call_error.uniqueId == "-1"
    # Unknown MessageType
    with pytest.raises(exceptions.OCPPException) as excinfo:
        serializer.parse_structure([666], protocol=protocol)
    assert excinfo.value.as_call_error.errorCode == msgtype_error
    assert excinfo.value.as_call_error.uniqueId == "-1"
    # Message too long
    with pytest.raises(exceptions.OCPPException) as excinfo:
        serializer.parse_structure([2, "19223201", "BootNotification", {}, "extra", "argument"], protocol=protocol)
    assert excinfo.value.as_call_error.errorCode == common_types.ErrorCodeEnum.ProtocolError
    assert excinfo.value.as_call_error.uniqueId == "-1"
    # Malformed message
    with pytest.raises(exceptions.OCPPException) as excinfo:
        serializer.parse_structure([2, 666, "this_is_crazy", "stop_this_folly"], protocol=protocol)
    assert excinfo.value.as_call_error.errorCode == common_types.ErrorCodeEnum.TypeConstraintViolation
    assert excinfo.value.as_call_error.uniqueId == "-1"
    # Exception can be converted to CallError
    assert excinfo.value.as_call_error == structure.CallError(
        uniqueId='-1',
        errorCode=common_types.ErrorCodeEnum.TypeConstraintViolation,
        errorDescription="Value '666' is not of type 'str' (type is 'int')",
        errorDetails={'value': 666, 'field': 'uniqueId'},
    )


@pytest.mark.parametrize('protocol,rpcframework_error,msgtype_error', [
    (compat.OcppJsonProtocol.v16, common_types.ErrorCodeEnum.GenericError, common_types.ErrorCodeEnum.GenericError),
    (
        compat.OcppJsonProtocol.v20,
        common_types.ErrorCodeEnum.RpcFrameworkError,
        common_types.ErrorCodeEnum.MessageTypeNotSupported,
    ),
])
def test_parse(mocker, protocol, rpcframework_error, msgtype_error):
    # Make sure the parser knows about our messages, bypassing selection made based on the protocol
    mocker.patch('ocpp_codec.compat.get_implemented_messages', return_value=messages.IMPLEMENTED)

    # Call
    call_msg = serializer.parse(
        [2, "19223201", "SimpleAction", {"value": "data", "validatedValue": "data", "enumValue": "Foo"}],
        protocol=protocol,
    )
    assert call_msg == structure.Call(
        uniqueId='19223201',
        action='SimpleAction',
        payload=messages.SimpleAction.req(value='data', validatedValue='data', enumValue=types.FooBarEnum.Foo),
    )

    # CallResult
    call_result_msg = serializer.parse(
        [3, "19223201", {"value": 12, "datetimeValue": "2019-01-30T12:30Z"}],
        # Provide the request's action name for appropriate parsing
        call_result_action_name=call_msg.action,
        protocol=protocol,
    )
    assert call_result_msg == structure.CallResult(
        uniqueId='19223201',
        payload=messages.SimpleAction.conf(
            value=12,
            datetimeValue=datetime.datetime(year=2019, month=1, day=30, hour=12, minute=30, tzinfo=pytz.UTC),
        ),
    )

    # CallError
    call_error_msg = serializer.parse(
        [4, "19223201", "GenericError", "What a tragedy", {"do_you_hear_me": "hey_ho"}],
        protocol=protocol,
    )
    assert call_error_msg == structure.CallError(
        uniqueId='19223201',
        errorCode=common_types.ErrorCodeEnum.GenericError,
        errorDescription='What a tragedy',
        errorDetails={'do_you_hear_me': 'hey_ho'},
    )

    # Empty payload as {} or null is ok
    call_msg = serializer.parse([2, "19223201", "NoPayloadAction", {}], protocol=protocol)
    assert call_msg == structure.Call(
        uniqueId='19223201',
        action='NoPayloadAction',
        payload=messages.NoPayloadAction.req(),
    )
    call_msg = serializer.parse([2, "19223201", "NoPayloadAction", None], protocol=protocol)
    assert call_msg == structure.Call(
        uniqueId='19223201',
        action='NoPayloadAction',
        payload=messages.NoPayloadAction.req(),
    )

    # Valid JSON but not OCPP-J
    with pytest.raises(exceptions.OCPPException) as excinfo:
        serializer.parse({"that_is_not": "ocpp-json"}, protocol=protocol)
    assert excinfo.value.as_call_error.errorCode == rpcframework_error
    assert excinfo.value.as_call_error.uniqueId == "-1"
    # Valid OCPP-J but empty list that we cannot guess anything from
    with pytest.raises(exceptions.OCPPException) as excinfo:
        serializer.parse([], protocol=protocol)
    assert excinfo.value.as_call_error.errorCode == rpcframework_error
    assert excinfo.value.as_call_error.uniqueId == "-1"
    # Unknown MessageType
    with pytest.raises(exceptions.OCPPException) as excinfo:
        serializer.parse([666], protocol=protocol)
    assert excinfo.value.as_call_error.errorCode == msgtype_error
    assert excinfo.value.as_call_error.uniqueId == "-1"
    # Malformed message
    with pytest.raises(exceptions.OCPPException) as excinfo:
        serializer.parse([2, 666, "this_is_crazy", "stop_this_folly"], protocol=protocol)
    assert excinfo.value.as_call_error.errorCode == common_types.ErrorCodeEnum.TypeConstraintViolation
    assert excinfo.value.as_call_error.uniqueId == "-1"
    # Invalid payload
    with pytest.raises(exceptions.OCPPException) as excinfo:
        serializer.parse([2, "19223201", "SimpleAction", {"not_the_right": "payload"}], protocol=protocol)
    # Exception can be converted to CallError
    assert excinfo.value.as_call_error == structure.CallError(
        uniqueId='19223201',
        errorCode=common_types.ErrorCodeEnum.ProtocolError,
        errorDescription="Missing or undefined/empty required fields",
        errorDetails={
            'required_fields': ['enumValue', 'validatedValue', 'value'],
            'provided_fields': ['not_the_right'],
        },
    )


def test_serialize_field(mocker):
    validated_field = fields(types.ValidatedType)[0]

    serialized_data = serializer.serialize_field(validated_field, 'good_value')
    assert serialized_data == 'good_value'

    with pytest.raises(errors.PropertyConstraintViolationError):
        serializer.serialize_field(validated_field, 'too_long' * 100)

    # Mimic a validator which doesn't return the appropriate type
    mock_validator = mocker.MagicMock(return_value=123)
    mock_metadata = mocker.MagicMock()
    mock_metadata.get = mocker.MagicMock(return_value=mock_validator)

    mocker.patch.object(validated_field, 'metadata', new=mock_metadata)
    with pytest.raises(errors.TypeConstraintViolationError):
        serializer.serialize_field(validated_field, 'good_value')

    # Check that a field with an encoder converts the type accordingly
    datetime_field = fields(types.DateTimeType)[0]
    date_string = serializer.serialize_field(
        datetime_field,
        datetime.datetime(year=2019, month=1, day=30, hour=12, minute=0, tzinfo=pytz.UTC),
    )
    assert date_string == '2019-01-30T12:00:00+00:00'

    # Not defining a validator is fine
    simple_field = fields(messages.SimpleAction.req)[0]
    data = 'Anything goooes!' * 100
    serialized_data = serializer.serialize_field(simple_field, data)
    assert serialized_data == data


def test_serialize_fields():
    # Simple message
    simple_req_msg = messages.SimpleAction.req(
        value='foo',
        validatedValue='bar',
        enumValue=types.FooBarEnum.Foo,
    )
    serialized_data = serializer.serialize_fields(simple_req_msg)
    assert serialized_data == {
        'value': 'foo',
        'validatedValue': 'bar',
        'enumValue': 'Foo',
    }
    simple_conf_msg = messages.SimpleAction.conf(
        value=12,
        datetimeValue=datetime.datetime(year=2019, month=1, day=30, hour=12, minute=0, tzinfo=pytz.UTC),
    )
    serialized_data = serializer.serialize_fields(simple_conf_msg)
    assert serialized_data == {
        'value': 12,
        'datetimeValue': '2019-01-30T12:00:00+00:00',
    }

    # More complex message, with lists and optional values
    complex_req_msg = messages.ComplexAction.req(
        complexValue=types.ComplexType(enumValue=types.FooBarEnum.Foo, validatedValue='data'),
        listValue=[
            types.ListElementType(
                datetimeValue=datetime.datetime(year=2019, month=1, day=30, hour=12, minute=0, tzinfo=pytz.UTC),
                nestedListValue=[
                    types.ElementType(value='foo'),
                    types.ElementType(value='bar', optionalValue=types.FooBarEnum.Bar),
                ],
            ),
            types.ListElementType(
                datetimeValue=datetime.datetime(year=2019, month=1, day=30, hour=12, minute=30, tzinfo=pytz.UTC),
                nestedListValue=[
                    types.ElementType(value='foobar'),
                ],
            ),
        ],
    )
    assert serializer.serialize_fields(complex_req_msg) == {
        'complexValue': {'enumValue': 'Foo', 'validatedValue': 'data'},
        'listValue': [
            {
                'datetimeValue': '2019-01-30T12:00:00+00:00', 'nestedListValue': [
                    {'value': 'foo'},
                    {'value': 'bar', 'optionalValue': 'Bar'},
                ],
            },
            {'datetimeValue': '2019-01-30T12:30:00+00:00', 'nestedListValue': [{'value': 'foobar'}]},
        ],
    }

    # Optional list field, not provided
    complex_conf_msg = messages.ComplexAction.conf()
    assert serializer.serialize_fields(complex_conf_msg) == {}

    # Optional list field, provided but empty
    complex_conf_msg = messages.ComplexAction.conf(optionalListValue=[])
    assert serializer.serialize_fields(complex_conf_msg) == {}

    # Optional list field, provided with some content
    complex_req_msg = messages.ComplexAction.conf(optionalListValue=['conf1', 'conf2'])
    assert serializer.serialize_fields(complex_req_msg) == {'optionalListValue': ['conf1', 'conf2']}

    # Test exceptions are propagated
    with pytest.raises(errors.PropertyConstraintViolationError):
        # 'validatedValue' is too long
        serializer.serialize_fields(messages.SimpleAction.req(
            value='data',
            validatedValue='data' * 100,
            enumValue=types.FooBarEnum.Foo,
        ))
    with pytest.raises(errors.TypeConstraintViolationError):
        # 'datetimeValue' isn't of the valid type
        serializer.serialize_fields(messages.SimpleAction.conf(
            value=12,
            datetimeValue=123,
        ))
    # Test missing required field
    with pytest.raises(errors.ProtocolError):
        # 'enumValue' is missing
        msg = messages.SimpleAction.req(value='data', validatedValue='data', enumValue=None)
        serializer.serialize_fields(msg)
    with pytest.raises(errors.ProtocolError):
        # Required non-empty list field, provided but empty
        serializer.serialize_fields(messages.ComplexAction.req(
            complexValue=types.ComplexType(enumValue=types.FooBarEnum.Foo, validatedValue='data'),
            listValue=[],
        ))
    with pytest.raises(errors.PropertyConstraintViolationError):
        # 'listValue' contains at most 4 elements
        dt = datetime.datetime(year=2019, month=1, day=30, hour=12, minute=0, tzinfo=pytz.UTC)
        serializer.serialize_fields(messages.ComplexAction.req(
            complexValue=types.ComplexType(enumValue=types.FooBarEnum.Foo, validatedValue='data'),
            listValue=[
                types.ListElementType(datetimeValue=dt, nestedListValue=[types.ElementType(value='first')]),
                types.ListElementType(datetimeValue=dt, nestedListValue=[types.ElementType(value='second')]),
                types.ListElementType(datetimeValue=dt, nestedListValue=[types.ElementType(value='third')]),
                types.ListElementType(datetimeValue=dt, nestedListValue=[types.ElementType(value='fourth')]),
                types.ListElementType(datetimeValue=dt, nestedListValue=[types.ElementType(value='extra_element')]),
            ],
        ))
    with pytest.raises(errors.PropertyConstraintViolationError):
        # List of complex types with a violated size constraint on the list itself.
        serializer.serialize_fields(messages.ComplexAction.conf(
            optionalComplexListValue=[
                types.ComplexType(enumValue=types.FooBarEnum.Foo, validatedValue='valid'),
            ] * 5,
        ))
    with pytest.raises(errors.PropertyConstraintViolationError):
        # List of complex types with a violated size constraint on the sole list's element.
        serializer.serialize_fields(messages.ComplexAction.conf(
            optionalComplexListValue=[
                types.ComplexType(enumValue=types.FooBarEnum.Foo, validatedValue='a' * 21),
            ],
        ))


def test_serialize():
    # Call
    call_msg = structure.Call(
        uniqueId='19223201',
        action='SimpleAction',
        payload=messages.SimpleAction.req(value='data', validatedValue='data', enumValue=types.FooBarEnum.Foo),
    )
    assert serializer.serialize(call_msg) == [2, "19223201", "SimpleAction", {
        "value": "data",
        "validatedValue": "data",
        "enumValue": "Foo",
    }]

    # CallResult
    call_result_msg = structure.CallResult(
        uniqueId='19223201',
        payload=messages.SimpleAction.conf(
            value=12,
            datetimeValue=datetime.datetime(year=2019, month=1, day=30, hour=12, minute=0, tzinfo=pytz.UTC),
        ),
    )
    assert serializer.serialize(call_result_msg) == [3, "19223201", {
        "value": 12,
        "datetimeValue": "2019-01-30T12:00:00+00:00",
    }]

    # CallError
    call_error_msg = structure.CallError(
        uniqueId='19223201',
        errorCode=common_types.ErrorCodeEnum.GenericError,
        errorDescription='What a tragedy',
        errorDetails={'do_you_hear_me': 'hey_ho'},
    )
    assert serializer.serialize(call_error_msg) == [
        4, "19223201", "GenericError", "What a tragedy", {"do_you_hear_me": "hey_ho"}
    ]
