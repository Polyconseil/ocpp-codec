# Copyright (c) Polyconseil SAS. All rights reserved.
"""This module contains errors raised during (de)serialization of OCPP messages.
"""


class OCPPException(Exception):
    """Exception wrapping a 'BaseOCPPError', tying it to a specific request.

    In OCPP, an error is always tied to a request. This exception ties a request to an error, and provides a
    ready-to-serialize 'CallError' object to send to the remote connection.

    Attributes:
        - ocpp_error: 'BaseOCPPError', the actual error
        - related_request_id: str, the uniqueId identifying the request this error is tied to, or "-1" if it's not tied
                              to any request (e.g.: could not read the message)
        - as_call_error: 'CallError', a ready-to-serialize OCPP message to send to the remote connection
    """

    def __init__(self, ocpp_error, related_request_id, *args, **kwargs):
        super().__init__(ocpp_error, related_request_id, *args, **kwargs)

        self.ocpp_error = ocpp_error
        self.related_request_id = related_request_id

        from .structure import CallError
        from .structure import MessageTypeEnum
        self._call_error = CallError(
            uniqueId=self.related_request_id,
            errorCode=self.ocpp_error.code,
            errorDescription=self.ocpp_error.msg,
            errorDetails=self.ocpp_error.details,
        )

    @property
    def as_call_error(self):
        return self._call_error
