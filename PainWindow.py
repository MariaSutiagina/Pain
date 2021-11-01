from PyQt5 import uic
from PyQt5.QtCore import QTranslator, QCoreApplication, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QButtonGroup
import os
from babel import Locale
from PainCanvas import Canvas

PICK_COLORS = [
    '#000000', '#82817f', '#820300', '#868417', '#007e03', '#037e7b', '#040079',
    '#81067a', '#7f7e45', '#05403c', '#0a7cf6', '#093c7e', '#7e07f9', '#7c4002',

    '#ffffff', '#c1c1c1', '#f70406', '#fffd00', '#08fb01', '#0bf8ee', '#0000fa',
    '#b92fc2', '#fffc91', '#00fd83', '#87f9f9', '#8481c4', '#dc137d', '#fb803c',
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
    

        