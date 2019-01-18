from plutter.text_model import TextModel


def init():
    global _text_model
    global _plugins
    global _prevent_gc_keep
    _text_model = TextModel()
    _plugins = []
    _prevent_gc_keep = []


def prevent_gc(keep):
    _prevent_gc_keep.append(keep)


def get_text_model():
    return _text_model


def get_client_id():
    return int(_text_model.client_id)


def set_client_id(client_id):
    _text_model.client_id = client_id


def add_plugin(plugin):
    _plugins.append(plugin)


def get_all_plugins():
    return _plugins
