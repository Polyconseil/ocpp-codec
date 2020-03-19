ocpp-codec - OCPP messages encoder-decoder
==========================================

*ocpp-codec* provides dataclasses definitions of OCPP messages and types, in both version 1.6 and 2.0 of the protocol.

It also provides a JSON pre-serializer and post-deserializer to exchange messages (see below).

It **does not** provide an API to write an OCPP server or client.

Pre-serializer
--------------

Turn an OCPP message dataclass instance into a basic Python dict representing the JSON payload:

.. code-block:: python

    import datetime
    import json

    from ocpp_codec import serializer
    from ocpp_codec import structure
    from ocpp_codec.v20 import messages
    from ocpp_codec.v20 import types

    response_payload = messages.BootNotification.Response(
        datetime.datetime(2013, 2, 1, 20, 53, 32, 486000, datetime.timezone.utc),
        300,
        types.RegistrationStatusEnum.Accepted,
    )
    call_result = structure.CallResult("19223201", response_payload)
    pre_serialized = serializer.serialize(call_result)

    print(pre_serialized)
    # [3, '19223201', {'currentTime': '2013-02-01T20:53:32.486000+00:00', 'interval': 300, 'status': 'Accepted'}]

    print(json.dumps(pre_serialized))
    # [3, "19223201", {"currentTime": "2013-02-01T20:53:32.486000+00:00", "interval": 300, "status": "Accepted"}]

As you can see in this example the pre-serialized data already converted ``datetime`` and ``enum.Enum`` fields to
strings. The result can then directly be given to ``json.dumps`` to get the JSON string to be sent as an RPC.

Post-deserializer
-----------------

Turn a Python dict (extracted from a JSON string) to an OCPP message dataclass:

.. code-block:: python

    import json

    from ocpp_codec import compat
    from ocpp_codec import serializer
    from ocpp_codec.v20 import messages

    deserialized = json.loads("""[3, "19223201", {"currentTime": "2013-02-01T20:53:32.486000+00:00", "interval": 300, "status": "Accepted"}]""")
    call_result = serializer.parse(deserialized, 'BootNotification', protocol=compat.OcppJsonProtocol.v20)

    print(call_result.uniqueId)
    # 19223201

    print(call_result.payload)
    # BootNotification.Response(currentTime=datetime.datetime(2013, 2, 1, 20, 53, 32, 486000, tzinfo=tzutc()), interval=300, status=<RegistrationStatusEnum.Accepted: 'Accepted'>)

As you can see in this example, the post-deserialized payload is a dataclass holding python data types such as ``datetime`` and ``enum.Enum``.
