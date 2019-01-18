import plutter
import json


class EngineMethodResult:

    def __init__(self, window, message):
        self.data = None
        self.window = window
        self.message = message

    # Sends a success response, indicating that the call completed successfully.
    # An optional value can be provided as part of the success message.
    def success(self, data):
        response_data = [data]
        plutter.send_platform_message_response(self.window, self.message, json.dumps(response_data))

    # Sends a not-implemented response, indicating that the method either was not
    # recognized, or has not been implemented.
    def not_implemented(self):
        plutter.send_platform_message_response(self.window, self.message, None)

    # Sends an error response, indicating that the call was understood but
    # handling failed in some way. A string error code must be provided, and in
    # addition an optional user-readable error_message and/or details object can
    # be included.
    def error(self, error_code, error_message, error_details):
        response_data = [{'code_code': error_code, 'error_message': error_message, 'error_details': error_details}]
        plutter.send_platform_message_response(self.window, self.message, json.dumps(response_data))
