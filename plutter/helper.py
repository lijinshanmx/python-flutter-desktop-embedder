import platform

import glfw


def log(message):
    print('plutter:===>%s' % message)


def get_flutter_engine_path():
    os_name = platform.system().lower()
    if os_name == 'darwin':
        flutter_engine_path = 'dependencies/flutter_engine'
    elif os_name == 'linux':
        flutter_engine_path = 'dependencies/libflutter_engine.so'
    elif os_name == 'windows':
        flutter_engine_path = 'dependencies/flutter_engine.dll'
    return flutter_engine_path


def is_control_or_command_key_down(mods):
    os_name = platform.system().lower()
    if os_name == 'darwin':
        return mods == glfw.MOD_SUPER
    else:
        return mods == glfw.MOD_CONTROL
