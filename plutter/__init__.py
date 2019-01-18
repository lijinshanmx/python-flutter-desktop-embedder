import json
import os
import time

import glfw
from cffi import FFI

import plutter.flutter_global
from plutter.engine_method_call import EngineMethodCall
from plutter.engine_method_result import EngineMethodResult
from plutter.helper import get_flutter_engine_path, is_control_or_command_key_down
from plutter.helper import log
from plutter.system_plugins import TextInputPlugin

kdp_per_inch = 160.0
ffi = FFI()
with open(os.path.join(os.getcwd(), 'plutter/flutter_embedder.h'), 'r') as fd:
    source = fd.read()
ffi.cdef(source)
flutter_global.init()
flutter_engine = ffi.dlopen(os.path.join(os.getcwd(), get_flutter_engine_path()))


def get_screen_coordinates_per_inch():
    primary_monitor = glfw.get_primary_monitor()
    primary_monitor_mode = glfw.get_video_mode(primary_monitor)
    primary_monitor_width_mm = ffi.new('int*')
    glfw.get_monitor_physical_size(primary_monitor, primary_monitor_width_mm, ffi.NULL)
    if primary_monitor_width_mm[0] == 0:
        return kdp_per_inch
    return primary_monitor_mode.width / (primary_monitor_width_mm[0] / 25.4)


@glfw._ffi.callback("void(GLFWwindow*,int,int)")
def glfw_framebuffer_size_callback(window, width_px, height_px):
    width = ffi.new('int*')
    glfw.get_window_size(window, width, ffi.NULL)
    state = get_saved_embedder_state(window)
    state.window_pixels_per_screen_coordinate = width_px / width[0]
    dpi = state.window_pixels_per_screen_coordinate * state.monitor_screen_coordinates_per_inch
    event = ffi.new('FlutterWindowMetricsEvent*')
    event.struct_size = ffi.sizeof('FlutterWindowMetricsEvent')
    event.width = width_px
    event.height = height_px
    event.pixel_ratio = dpi / kdp_per_inch
    log('pixel_ratio:%s' % event.pixel_ratio)
    flutter_engine.FlutterEngineSendWindowMetricsEvent(state.engine, event)


@glfw._ffi.callback("void(GLFWwindow *, int, int, int, int)")
def glfw_key_callback(window, key, scancode, action, mods):
    if action == glfw.REPEAT or action == glfw.PRESS:
        text_model = flutter_global.get_text_model()
        if text_model.client_id != 0:
            if key == glfw.KEY_ENTER:
                if is_control_or_command_key_down(mods):
                    perform_action(window, 'done')
                else:
                    text_model.add_char('\n')
                    perform_action(window, 'newline')
            elif key == glfw.KEY_HOME:
                text_model.move_cursor_home(mods)
            elif key == glfw.KEY_END:
                text_model.move_cursor_end(mods)
            elif key == glfw.KEY_LEFT:
                text_model.move_cursor_left(mods)
            elif key == glfw.KEY_RIGHT:
                text_model.move_cursor_right(mods)
            elif key == glfw.KEY_DELETE:
                pass
            elif key == glfw.KEY_BACKSPACE:
                text_model.backspace(mods)
            elif key == glfw.KEY_A:
                if is_control_or_command_key_down(mods):
                    text_model.select_all()
            elif key == glfw.KEY_C:
                if is_control_or_command_key_down(mods) and text_model.is_selected():
                    _, _, selected_content = text_model.get_selected_text()
                    clipboard_data = ffi.new('char[]', selected_content.encode('utf-8'))
                    glfw.set_clipboard_string(window, clipboard_data)
            elif key == glfw.KEY_X:
                if is_control_or_command_key_down(mods) and text_model.is_selected():
                    _, _, selected_content = text_model.get_selected_text()
                    clipboard_data = ffi.new('char[]', selected_content.encode('utf-8'))
                    glfw.set_clipboard_string(window, clipboard_data)
                    text_model.remove_selected_text()
            elif key == glfw.KEY_V:
                if is_control_or_command_key_down(mods):
                    clipboard_string = glfw.get_clipboard_string(window).decode('utf-8')
                    text_model.add_char(clipboard_string)


@glfw._ffi.callback("void(GLFWwindow *, unsigned int)")
def glfw_Char_Callback(window, rune):
    log('input char: %c' % chr(rune))
    flutter_global.get_text_model().add_char(chr(rune))


@glfw._ffi.callback("void(GLFWwindow*,int,int,int)")
def glfw_mouse_button_callback(window, key, action, mods):
    x = ffi.new('double*')
    y = ffi.new('double*')
    if key == glfw.MOUSE_BUTTON_1 and action == glfw.PRESS:
        glfw.get_cursor_pos(window, x, y)
        """log click position"""
        log('click pos: x=%s ,y=%s' % (x[0], y[0]))
        cursor_position_callback_at_phase(window, 2, x[0], y[0])
        glfw.set_cursor_pos_callback(window, cursor_position_callback)

    if key == glfw.MOUSE_BUTTON_1 and action == glfw.RELEASE:
        glfw.get_cursor_pos(window, x, y)
        cursor_position_callback_at_phase(window, 1, x[0], y[0])
        glfw.set_cursor_pos_callback(window, ffi.NULL)


@glfw._ffi.callback("void(GLFWwindow *, double, double)")
def cursor_position_callback(window, x, y):
    cursor_position_callback_at_phase(window, 3, x, y)


###############################################################################
# When GLFW calls back to the window with a cursor position move, forwards to
# FlutterEngine as a pointer event with appropriate phase.
###############################################################################
def cursor_position_callback_at_phase(window, phase, x, y):
    state = get_saved_embedder_state(window)
    event = ffi.new('FlutterPointerEvent*')
    event.struct_size = ffi.sizeof('FlutterPointerEvent')
    event.phase = phase
    event.x = x * state.window_pixels_per_screen_coordinate
    event.y = y * state.window_pixels_per_screen_coordinate
    event.timestamp = int(time.time())
    flutter_engine.FlutterEngineSendPointerEvent(state.engine, event, 1)


def glfw_assign_event_callbacks(window):
    glfw.poll_events()

    glfw.set_key_callback(window, glfw_key_callback)
    glfw.set_char_callback(window, glfw_Char_Callback)
    glfw.set_mouse_button_callback(window, glfw_mouse_button_callback)


@ffi.callback("bool(void *)")
def make_current(user_data):
    glfw.make_context_current(user_data)
    return True


@ffi.callback("bool(void *)")
def clear_current(_):
    glfw.make_context_current(ffi.NULL)
    return True


@ffi.callback("bool(void *)")
def present(user_data):
    glfw.swap_buffers(user_data)
    return True


@ffi.callback("uint32_t(void *)")
def fbo_callback(_):
    return 0


@ffi.callback("void(FlutterPlatformMessage *, void *)")
def flutter_platform_message_callback(message, user_data):
    if message.struct_size != ffi.sizeof('FlutterPlatformMessage'):
        return
    window = glfw._ffi.cast('GLFWwindow*', user_data)
    channel = ffi.string(message.channel).decode()
    message_content = ffi.string(message.message)
    log('channel:' + channel)
    log(message_content)

    for plugin in flutter_global.get_all_plugins():
        if channel == plugin.channel_name:
            json_message = json.loads(ffi.string(message.message, message.message_size))
            method_call = EngineMethodCall(json_message['method'], json_message['args'])
            result = EngineMethodResult(window, message)
            plugin.handle_method_call(method_call, result)


def get_saved_embedder_state(window):
    user_pointer = glfw.get_window_user_pointer(window)
    return ffi.cast('FlutterEmbedderState*', user_pointer)


def flutter_init():
    return glfw.init()


def flutter_terminate():
    glfw.terminate()


def create_flutter_window(initial_width, initial_height, main_path, assets_path, packages_path, icu_data_path
                          ):
    """window"""
    window = glfw.create_window(initial_width, initial_height, "Flutter", None, None)
    if not window:
        return None
    """engine"""
    engine = run_flutter_engine(window, main_path, assets_path, packages_path, icu_data_path)
    if not engine:
        return None
    """state"""
    state = ffi.new('FlutterEmbedderState*')
    """防止state被gc掉"""
    flutter_global.prevent_gc(state)
    flutter_global.get_text_model().notifyState = lambda: update_editing_state(window)
    state.engine = engine
    glfw.set_window_user_pointer(window, state)
    state.monitor_screen_coordinates_per_inch = get_screen_coordinates_per_inch()
    width_px = ffi.new('int*')
    height_px = ffi.new('int*')
    glfw.get_framebuffer_size(window, width_px, height_px)
    glfw.set_framebuffer_size_callback(window, glfw_framebuffer_size_callback)
    glfw_framebuffer_size_callback(window, width_px[0], height_px[0])

    glfw_assign_event_callbacks(window)
    return window


def create_flutter_window_in_snapshot_mode(initial_width, initial_height, assets_path, icu_data_path):
    return create_flutter_window(initial_width, initial_height, "", assets_path, "",
                                 icu_data_path)


def flutter_window_loop(flutter_window):
    while not glfw.window_should_close(flutter_window):
        glfw.wait_events()
    """FlutterEngineShutdown"""
    glfw.destroy_window(flutter_window)


def run_flutter_engine(window, main_path, assets_path, packages_path, icu_data_path):
    """FlutterRendererConfig"""
    config = ffi.new("FlutterRendererConfig*")
    config.type = flutter_engine.kOpenGL
    size = ffi.sizeof('FlutterOpenGLRendererConfig')
    config.open_gl.struct_size = size
    config.open_gl.make_current = make_current
    config.open_gl.clear_current = clear_current
    config.open_gl.present = present
    config.open_gl.fbo_callback = fbo_callback

    """FlutterProjectArgs"""
    args = ffi.new('FlutterProjectArgs*')
    assets_path = ffi.new('char[]', assets_path.encode('utf-8'))
    icu_data_path = ffi.new('char[]', icu_data_path.encode('utf-8'))
    packages_path = ffi.new('char[]', packages_path.encode('utf-8'))
    main_path = ffi.new('char[]', main_path.encode('utf-8'))
    args.assets_path = assets_path
    args.struct_size = ffi.sizeof('FlutterProjectArgs')
    args.icu_data_path = icu_data_path
    args.packages_path = packages_path
    args.main_path = main_path
    args.platform_message_callback = flutter_platform_message_callback

    """flutter engine"""
    engine = ffi.new('FlutterEngine*')
    result = flutter_engine.FlutterEngineRun(1, config, args, window, engine)
    if result != 0:
        return None
    return engine[0]


def add_plugin(plugin):
    flutter_global.add_plugin(plugin)


def send_platform_message_response(window, message, data):
    state = get_saved_embedder_state(window)
    response_data = ffi.new('char[]', data.encode('utf-8')) if data else ffi.NULL
    response_data_size = ffi.sizeof(response_data) - 1 if data else 0
    flutter_engine.FlutterEngineSendPlatformMessageResponse(state.engine,
                                                            message.response_handle,
                                                            response_data,
                                                            response_data_size)


def send_platform_message(window, message):
    state = get_saved_embedder_state(window)
    flutter_engine.FlutterEngineSendPlatformMessage(state.engine, message)


def update_editing_state(window):
    flutter_platform_message = ffi.new('FlutterPlatformMessage*')
    flutter_platform_message.channel = ffi.new('char[]', b'flutter/textinput')
    text_model = flutter_global.get_text_model()
    message_dict = {'method': 'TextInputClient.updateEditingState',
                    'args': [flutter_global.get_client_id(),
                             {'text': text_model.word,
                              'selectionBase': text_model.selection_base,
                              'selectionExtent': text_model.selection_extent,
                              'selectionAffinity': 'TextAffinity.downstream',
                              'selectionIsDirectional': False,
                              'composingBase': 0,
                              'composingExtent': 0
                              }
                             ]
                    }

    message = ffi.new('char[]', json.dumps(message_dict).encode('utf-8'))
    flutter_platform_message.message = message
    flutter_platform_message.message_size = ffi.sizeof(message) - 1
    flutter_platform_message.struct_size = ffi.sizeof('FlutterPlatformMessage')
    send_platform_message(window, flutter_platform_message)


def perform_action(window, action):
    flutter_platform_message = ffi.new('FlutterPlatformMessage*')
    flutter_platform_message.channel = ffi.new('char[]', b'flutter/textinput')
    message_dict = {'method': 'TextInputClient.performAction',
                    'args': [flutter_global.get_client_id(),
                             'TextInputAction.%s' % action
                             ]
                    }
    message = ffi.new('char[]', json.dumps(message_dict).encode())
    flutter_platform_message.message = message
    flutter_platform_message.message_size = ffi.sizeof(message) - 1
    flutter_platform_message.struct_size = ffi.sizeof('FlutterPlatformMessage')
    send_platform_message(window, flutter_platform_message)
