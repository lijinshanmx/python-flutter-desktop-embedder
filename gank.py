import plutter
import os

from plugins import TestPlugin
from plutter import TextInputPlugin
from plutter.system_plugins import FlutterPlatformPlugin

assets_path = '/Users/lijinshan/Desktop/flutter_assets'
icu_data_path = os.path.join(os.getcwd(), 'dependencies/icudtl.dat')


def main():
    if not plutter.flutter_init():
        print("Couldn't init GLFW")
        return

    window = plutter.create_flutter_window_in_snapshot_mode(400, 800, assets_path, icu_data_path, None)
    # add system plugins
    plutter.add_plugin(TextInputPlugin())
    plutter.add_plugin(FlutterPlatformPlugin())
    # add user plugins
    plutter.add_plugin(TestPlugin())
    if not window:
        print("Couldn't create Window")
        plutter.flutter_terminate()
        return
    plutter.flutter_window_loop(window)
    plutter.flutter_terminate()


# run
main()
