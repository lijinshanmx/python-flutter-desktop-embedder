import glfw
from cffi import FFI

from plutter import flutter_global
from plutter.base_plugin import BasePlugin


class TextInputPlugin(BasePlugin):
    channel_name = 'flutter/textinput'

    def handle_method_call(self, method_call, result):
        text_model = flutter_global.get_text_model()
        if method_call.method == 'TextInput.clearClient':
            text_model.client_id = 0
        elif method_call.method == 'TextInput.setClient':
            flutter_global.set_client_id(method_call.arguments[0])
        elif method_call.method == 'TextInput.setEditingState':
            if text_model.client_id != 0:
                text_model.word = method_call.arguments['text']
                text_model.selection_base = method_call.arguments['selectionBase']
                text_model.selection_extent = method_call.arguments['selectionExtent']
        else:
            result.not_implemented()


class FlutterPlatformPlugin(BasePlugin):
    channel_name = 'flutter/platform'

    def handle_method_call(self, method_call, result):
        if method_call.method == 'Clipboard.getData':
            clipboard_string = glfw.get_clipboard_string(result.window)
            clipboard_data = {'text': clipboard_string.decode('utf-8')}
            result.success(clipboard_data)
        elif method_call.method == 'Clipboard.setData':
            ffi = FFI()
            clipboard_data = ffi.new('char[]', method_call.arguments['text'].encode('utf-8'))
            glfw.set_clipboard_string(result.window, clipboard_data)
        else:
            result.not_implemented()
