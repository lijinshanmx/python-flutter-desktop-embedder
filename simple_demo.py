import os

import plutter
from plutter import TextInputPlugin
from plutter.base_plugin import BasePlugin
from plutter.system_plugins import FlutterPlatformPlugin

assets_path = os.path.join(os.getcwd(), 'examples/simple_demo/build/flutter_assets')
icu_data_path = os.path.join(os.getcwd(), 'dependencies/icudtl.dat')


class SimpleDemoPlugin(BasePlugin):
    channel_name = 'simple_demo_plugin'

    def handle_method_call(self, method_call, result):
        if method_call.method == 'getTheValue':
            result.success('can be nums,bool or string')
        elif method_call.method == 'getListValue':
            result.success([1, 2, 3, 4])
        elif method_call.method == 'getDictValue':
            result.success({'value': 'dict value'})
        else:
            result.not_implemented()


def main():
    if not plutter.flutter_init():
        print("Couldn't init GLFW")
        return
    window = plutter.create_flutter_window_in_snapshot_mode(600, 600, assets_path, icu_data_path)
    # add system plugins
    plutter.add_plugin(TextInputPlugin())
    plutter.add_plugin(FlutterPlatformPlugin())
    # add user plugins
    plutter.add_plugin(SimpleDemoPlugin())
    if not window:
        print("Couldn't create Window")
        plutter.flutter_terminate()
        return
    plutter.flutter_window_loop(window)
    plutter.flutter_terminate()


# run
main()
