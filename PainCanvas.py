from PyQt5.QtWidgets import QLabel


class Canvas(QLabel):

    mode = 'rectangle'

    def initialize(self):
        pass

    def set_mode(self, mode):
        # Установить новый режим
        self.mode = mode
