class TextModel:
    ModNone = 0
    ModShift = 1
    ModControl = 2
    ModShiftControl = 3
    ModAlt = 4
    ModSuper = 8

    def __init__(self):
        self.client_id = 0
        self.word = ''
        self.selection_base = 0
        self.selection_extent = 0
        self.notifyState = None

    def is_selected(self):
        if self.client_id == 0:
            return False
        return self.selection_base != self.selection_extent

    def add_char(self, chars):
        if self.client_id == 0:
            return
        self.remove_selected_text()
        selection_base = self.selection_base
        selection_extent = self.selection_extent
        new_word = self.word[:selection_base] + chars + self.word[selection_extent:]
        self.word = new_word
        self.selection_base += len(chars)
        self.selection_extent = self.selection_base
        self.notifyState()

    def remove_selected_text(self):
        if self.client_id == 0:
            return False
        if self.is_selected():
            selection_index_start, selection_index_end, _ = self.get_selected_text()
            self.word = self.word[
                        :selection_index_start] + self.word[
                                                  selection_index_end:]
            self.selection_base = selection_index_start
            self.selection_extent = selection_index_start
            self.selection_extent = self.selection_base
            self.notifyState()
            return True
        return False

    def get_selected_text(self):
        if self.client_id == 0:
            return None
        if self.selection_base > self.selection_extent:
            selection_index_start = self.selection_extent
            selection_index_end = self.selection_base
        else:
            selection_index_start = self.selection_base
            selection_index_end = self.selection_extent
        return selection_index_start, selection_index_end, self.word[
                                                           selection_index_start:selection_index_end]

    def move_cursor_home(self, mods):
        self.selection_base = 0
        if mods != TextModel.ModShift:
            self.selection_extent = self.selection_base
        self.notifyState()

    def move_cursor_end(self, mods):
        self.selection_base = len(self.word)
        if mods != TextModel.ModShift:
            self.selection_extent = self.selection_base
        self.notifyState()

    def move_cursor_left(self, mods):
        if mods == TextModel.ModShiftControl or mods == TextModel.ModControl:
            self.selection_base = self.index_start_leading_word(self.word, self.selection_base)
        elif self.selection_base > 0:
            if mods != TextModel.ModShift and self.is_selected():
                self.selection_base, _, _ = self.get_selected_text()
            else:
                self.selection_base -= 1
        if mods == TextModel.ModNone or mods == TextModel.ModControl:
            self.selection_extent = self.selection_base

        self.notifyState()

    def move_cursor_right(self, mods):
        if mods == TextModel.ModShiftControl or mods == TextModel.ModControl:
            self.selection_base = self.index_end_forward_word(self.word, self.selection_base)
        elif self.selection_base < len(self.word):
            if mods != TextModel.ModShift and self.is_selected():
                _, self.selection_base, _ = self.get_selected_text()
            else:
                self.selection_base += 1
        if mods == TextModel.ModNone or mods == TextModel.ModControl:
            self.selection_extent = self.selection_base
        self.notifyState()

    def select_all(self):
        self.selection_base = 0
        self.selection_extent = len(self.word)
        self.notifyState()

    def delete(self, mods):
        if self.remove_selected_text():
            self.notifyState()
            return
        if self.selection_base < len(self.word):
            self.word = self.word[:self.selection_base] + self.word[self.selection_base + 1:]
            self.notifyState()

    def backspace(self, mods):
        if self.remove_selected_text():
            self.notifyState()
            return
        if len(self.word) > 0 and self.selection_base > 0:
            if mods == TextModel.ModControl:
                delete_up_to = self.index_start_leading_word(self.word, self.selection_base)
                self.word = self.word[:delete_up_to] + self.word[self.selection_base:]
                self.selection_base = delete_up_to
                self.selection_extent = delete_up_to
                self.notifyState()
            else:
                self.word = self.word[:self.selection_base - 1] + self.word[self.selection_base:]
                if self.selection_base > 0:
                    self.selection_base -= 1
                self.selection_extent = self.selection_base
                self.notifyState()

    @staticmethod
    def index_end_forward_word(line, start):
        pos = start
        line_size = len(line)
        while True:
            if pos == line_size or not line[pos].isspace():
                break
            pos += 1
        while True:
            if pos == line_size or line[pos].isspace():
                break
            pos += 1
        return pos

    @staticmethod
    def index_start_leading_word(line, start):
        pos = start
        hah = ''
        hah.isspace()
        while True:
            if pos == 0 or not line[pos - 1].isspace():
                break
            pos -= 1
        while True:
            if pos == 0 or line[pos - 1].isspace():
                break
            pos -= 1
        return pos
