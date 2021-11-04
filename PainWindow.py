from PyQt5 import uic
from PyQt5.QtCore import QTranslator, QCoreApplication, Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QButtonGroup, QColorDialog
import os
from babel import Locale
from PainCanvas import Canvas

import types

PICK_COLORS = [
    '#000000', '#82817e', '#820301', '#868416', '#007e02', '#037e7a', '#04007a',
    '#81067b', '#7f7e46', '#05403d', '#0a7cf7', '#093c7f', '#7e07f8', '#7c4003',

    '#ffffff', '#c2c2c2', '#f70405', '#fffd01', '#08fb00', '#0bf8ef', '#0000fb',
    '#b92fc3', '#fffc90', '#00fd82', '#87f9fa', '#8481c5', '#dc137e', '#fb803d',
]

BTN_MODES = [
    'selectPolygon', 'selectRectangular',
    'eraser', 'fill',
    'dropper', 'stamp',
    'pen', 'brush',
    'spray', 'text',
    'line', 'polyLine',
    'rectangle', 'polygon',
    'ellipse', 'roundRectangle'
]

class QPainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(QPainWindow, self).__init__(parent)
        uic.loadUi('resources/painwindow.ui', self)

        self.init_languages()
        self.init_colors()
        self.init_canvas()
        self.init_mode_buttons()
        self.init_color_selection()
        self.init_color_buttons()
        self.init_canvas_timer()
        self.init_clipboard_copy_button()
        self.show()

    def init_canvas(self):
        self.horizontalLayout.removeWidget(self.canvas)
        self.canvas = Canvas()
        self.canvas.initialize()
        self.horizontalLayout.addWidget(self.canvas)

    def init_mode_buttons(self):
        # Setup the mode buttons
        mode_group = QButtonGroup(self)
        mode_group.setExclusive(True)

        for mode in BTN_MODES:
            btn = getattr(self, f'{mode}Button')
            btn.pressed.connect(lambda mode=mode: self.canvas.set_mode(mode))
            mode_group.addButton(btn)

    def init_clipboard_copy_button(self):
        self.actionCopy.triggered.connect(self.copy_to_clipboard)

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()

        if self.canvas.mode == 'selectRectangular' and self.canvas.locked:
            clipboard.setPixmap(self.canvas.selectRectangular_copy())

        elif self.canvas.mode == 'selectPolygon' and self.canvas.locked:
            clipboard.setPixmap(self.canvas.selectPolygon_copy())

        else:
            clipboard.setPixmap(self.canvas.pixmap())

    def init_colors(self):
        for index, color in enumerate(PICK_COLORS, 1):
            btn = getattr(self, 'colorButton_%d' % index)
            btn.setStyleSheet('QPushButton { background-color: %s; }' % color)
            btn.hex = color  

    def init_languages(self):
        self.load_language_files()

        self.translator = QTranslator(self)
        locale = Locale.default()
        self.set_current_language(locale)

    def init_color_selection(self):
        # Setup the color selection buttons.
        self.primaryColorButton.pressed.connect(lambda: self.choose_color(self.set_primary_color))
        self.secondaryColorButton.pressed.connect(lambda: self.choose_color(self.set_secondary_color))

        # Setup to agree with Canvas.
        self.set_primary_color('#000000')
        self.set_secondary_color('#ffffff')

        # Signals for canvas-initiated color changes (dropper).
        self.canvas.primary_color_updated.connect(self.set_primary_color)
        self.canvas.secondary_color_updated.connect(self.set_secondary_color)

    def set_primary_color(self, color):
        self.canvas.set_primary_color(color)
        self.primaryColorButton.setStyleSheet('QPushButton { background-color: %s; }' % color)

    def set_secondary_color(self, color):
        self.canvas.set_secondary_color(color)
        self.secondaryColorButton.setStyleSheet('QPushButton { background-color: %s; }' % color)

    def choose_color(self, callback):
        dlg = QColorDialog()
        if dlg.exec():
            callback( dlg.selectedColor().name() )


    def init_color_buttons(self):
        # Инициализируем обработчики кнопок с палитрой
        for n, color in enumerate(PICK_COLORS, 1):
            btn = getattr(self, 'colorButton_%d' % n)
            btn.setStyleSheet('QPushButton { background-color: %s; }' % color)
            btn.hex = color  # For use in the event below

            def patch_mousePressEvent(self_, e):
                if e.button() == Qt.LeftButton:
                    self.set_primary_color(self_.hex)

                elif e.button() == Qt.RightButton:
                    self.set_secondary_color(self_.hex)

            btn.mousePressEvent = types.MethodType(patch_mousePressEvent, btn)

    def init_canvas_timer(self):
        self.canvas_timer = QTimer()
        self.canvas_timer.timeout.connect(self.canvas.on_timer)
        self.canvas_timer.setInterval(100)
        self.canvas_timer.start()

    def load_current_language(self, fn):
        app = QApplication.instance()
        if os.path.isfile(fn):
            if self.translator.load(fn):
              app.installTranslator(self.translator)
        else:
            app.removeTranslator(self.translator)
        self.retranslateUi(self)
        
    def set_current_language(self, locale):
        lang_path = os.path.join(self.get_lang_dir(),f'{locale.language}-{locale.territory}.qm')
        self.load_current_language(lang_path)

    def select_lang_func(self, tr):
        sender = self.sender()
        self.load_current_language(sender.data())
   

    def add_lang_menu(self, ln, fn):
        langAct = QAction(ln, self)
        langAct.setData(fn)
        langAct.triggered.connect(self.select_lang_func)
        self.menuLanguage.addAction(langAct)

    def get_lang_dir(self):
        return os.path.join(os.path.dirname(__file__),'resources/lang')

    def load_language_files(self):
        lang_dir = self.get_lang_dir()
        for file in os.listdir(lang_dir):
            fn = os.fsdecode(file)
            if fn.endswith('.qm'):
                ll = fn[:-3]
                lp = ll.split('-')
                ln = Locale(lp[0], lp[1])
                self.add_lang_menu(ln.display_name, os.path.join(lang_dir,fn))

    def retranslateUi(self, wnd):
        _translate = QCoreApplication.translate
        wnd.setWindowTitle(_translate("PainWindow", "Pain"))
        self.menuFile.setTitle(_translate("PainWindow", "File"))
        self.menuEdit.setTitle(_translate("PainWindow", "Edit"))
        self.menuImage.setTitle(_translate("PainWindow", "Image"))
        self.menuTools.setTitle(_translate("PainWindow", "Tools"))
        self.menuLanguage.setTitle(_translate("PainWindow", "Language..."))
        self.menuHelp.setTitle(_translate("PainWindow", "Help"))
        self.fileToolbar.setWindowTitle(_translate("PainWindow", "toolBar"))
        self.drawingToolbar.setWindowTitle(_translate("PainWindow", "toolBar"))
        self.fontToolbar.setWindowTitle(_translate("PainWindow", "toolBar"))
        self.actionCopy.setText(_translate("PainWindow", "Copy"))
        self.actionCopy.setShortcut(_translate("PainWindow", "Ctrl+C"))
        self.actionClearImage.setText(_translate("PainWindow", "Clear Image"))
        self.actionOpenImage.setText(_translate("PainWindow", "Open Image..."))
        self.actionSaveImage.setText(_translate("PainWindow", "Save Image As..."))
        self.actionInvertColors.setText(_translate("PainWindow", "Invert Colors"))
        self.actionFlipHorizontal.setText(_translate("PainWindow", "Flip Horizontal"))
        self.actionFlipVertical.setText(_translate("PainWindow", "Flip Vertical"))
        self.actionNewImage.setText(_translate("PainWindow", "New Image"))
        self.actionBold.setText(_translate("PainWindow", "Bold"))
        self.actionBold.setShortcut(_translate("PainWindow", "Ctrl+B"))
        self.actionItalic.setText(_translate("PainWindow", "Italic"))
        self.actionItalic.setShortcut(_translate("PainWindow", "Ctrl+I"))
        self.actionUnderline.setText(_translate("PainWindow", "Underline"))
        self.actionFillShapes.setText(_translate("PainWindow", "Fill Shapes?"))
    

        