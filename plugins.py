from plutter.base_plugin import BasePlugin


class TestPlugin(BasePlugin):
    channel_name = 'Test_Plugin'

    def handle_method_call(self, method_call, result):
        result.success('success')
