Changelog
=========

0.2.1 (unreleased)
------------------

- Nothing changed yet.


0.2.0 (2020-06-01)
------------------

- New: Add a dedicated 'encoder' metadata attribute on fields instead of mixing it with validators.
- Fix: Limit decimal values to 6 places when sending a value to a charging station
- New: Add usage examples to README.rst.
- Technical: Make OCPPMessage.messageTypeId a class attribute to make instantiation easier.
- Fix: Serialization of List[non-ComplexType] fields.
- New: Add OCPP 2.0 messages: TransactionEvent.{Request,Response} and underlying messages.


0.1.4 (2020-02-28)
------------------

- Fix: Change DataTransfer.{req,conf}.data to str instead of bytes (OCPP 1.6)


0.1.3 (2020-02-17)
------------------

- Fix: OCPP 2.0 enum types are now correctly defined and parsed.
- New: Add new OCPP 2.0 messages: ChangeAvailability, GetVariables and SetVariables.


0.1.2 (2020-02-13)
------------------

- Technical: Introduce zest.releaser
- Fix: Include dataclasses dependency for python 3.6
- Technical: Move from pyproject.toml to setup.cfg


0.1.1 (2020-10-15)
------------------

- Fix: Change Python requirement to include >=3.6


0.1.0 (2020-10-01)
------------------

- Initial release
