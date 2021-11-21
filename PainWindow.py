from PyQt5 import uic
from PyQt5.QtCore import  QCoreApplication, Qt, QTimer,QRect, QPoint
from PyQt5.QtGui import QPixmap,QImage,QTransform,QIcon, QFont
from PyQt5.QtWidgets import QMainWindow,  QButtonGroup, QColorDialog, QFileDialog, QFontComboBox, QComboBox, QLabel, QSlider
from PainCanvas import Canvas

from FractalDialog import QFractalDialog

import types
import utils

PICK_COLORS = [
    '#000000', '#82817e', '#820301', '#868416', '#007e02', '#037e7a', '#04007a',
    '#81067b', '#7f7e46', '#05403d', '#0a7cf7', '#093c7f', '#7e07f8', '#7c4003',

    '#ffffff', '#c2c2c2', '#f70405', '#fffd01', '#08fb00', '#0bf8ef', '#0000fb',
    '#b92fc3', '#fffc90', '#00fd82', '#87f9fa', '#8481c5', '#dc137e', '#fb803d',
]

BTN_MODES = [
    # 'selectPolygon', 'selectRectangular',
    'eraser', 'fill',
    'pipette', 'stamp',
    'pen', 'brush',
    'spray', 'text',
    'line', 'polyLine',
    'rectangle', 'polygon',
    'ellipse', 'roundRectangle'
]

BOUNDS_OF_CANVAS = 600, 400

FONT_SIZES = [7, 8, 9, 10, 11, 12, 13, 14, 18, 24, 36, 48, 64, 72, 96, 144]


STAMPS = [
':/stamps/drw-1.jpg',
':/stamps/drw-box.jpg',
':/stamps/drw-cyber.jpg',
':/stamps/drw-dalek.jpg',
':/stamps/drw-gear.jpg',
':/stamps/drw-magic.jpg',
':/stamps/drw-space.jpg',
':/stamps/drw-tiktok.jpg',

]
class QPainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(QPainWindow, self).__init__(parent)
        uic.loadUi(utils.resource_path('resources/painwindow.ui'), self)

        # self.init_languages()
        self.init_colors()
        self.init_canvas()
        self.init_mode_buttons()
        self.init_event_props()
        self.init_color_selection()
        self.init_color_buttons()
        self.init_canvas_timer()
        # self.init_clipboard_copy_button()
        self.init_menu()
        self.init_stamps()
        self.init_font_toolbar()
        self.init_size_toolbar()

        self.show()

    def resizeEvent(self, event):
        QMainWindow.resizeEvent(self, event)
        self.canvas.resize(event.size())

    def init_font_toolbar(self):
        # Setup the drawing toolbar.
        self.fontselect = QFontComboBox()
        self.fontToolbar.addWidget(self.fontselect)
        self.fontselect.currentFontChanged.connect(lambda f: self.canvas.set_options('font', f))
        self.fontselect.setCurrentFont(QFont('Times'))

        self.fontsize = QComboBox()
        self.fontsize.addItems([str(s) for s in FONT_SIZES])
        self.fontsize.currentTextChanged.connect(lambda f: self.canvas.set_options('fontsize', int(f)))

        # Connect to the signal producing the text of the current selection. Convert the string to float
        # and set as the pointsize. We could also use the index + retrieve from FONT_SIZES.
        self.fontToolbar.addWidget(self.fontsize)

        self.fontToolbar.addAction(self.actionBold)
        self.actionBold.triggered.connect(lambda s: self.canvas.set_options('bold', s))
        self.fontToolbar.addAction(self.actionItalic)
        self.actionItalic.triggered.connect(lambda s: self.canvas.set_options('italic', s))
        self.fontToolbar.addAction(self.actionUnderline)
        self.actionUnderline.triggered.connect(lambda s: self.canvas.set_options('underline', s))

    def init_size_toolbar(self):
        sizeicon = QLabel()
        sizeicon.setPixmap(QPixmap(':/icons/border-weight.png'))
        self.drawingToolbar.addWidget(sizeicon)
        self.sizeselect = QSlider()
        self.sizeselect.setRange(1,20)
        self.sizeselect.setOrientation(Qt.Horizontal)
        self.sizeselect.valueChanged.connect(lambda s: self.canvas.set_options('size', s))
        self.drawingToolbar.addWidget(self.sizeselect)

        self.actionFillShapes.triggered.connect(lambda s: self.canvas.set_options('fill', s))
        self.drawingToolbar.addAction(self.actionFillShapes)
        self.actionFillShapes.setChecked(True)

    def init_menu(self):
        self.actionNewImage.triggered.connect(self.canvas.initialize)
        self.actionOpenImage.triggered.connect(self.file_open)
        self.actionSaveImage.triggered.connect(self.file_save)
        self.actionClearImage.triggered.connect(self.canvas.reset)
        self.actionInvertColors.triggered.connect(self.invert)
        self.actionFlipHorizontal.triggered.connect(self.flip_horz)
        self.actionFlipVertical.triggered.connect(self.flip_vert)
        self.actionFractal.triggered.connect(self.fractal)

    def file_open(self):
        """
        Открывает изображение для редактирования.
        Масштабирует по меньшему размеру, остаток - обрезает
        :return:
        """
        path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Файлы PNG (*.png); Файлы JPEG (*jpg); Все файлы (*.*)")

        if path:
            pixmap = QPixmap()
            pixmap.load(path)

            # Получаем размер загруженного изображения
            iw = pixmap.width()
            ih = pixmap.height()

            # Получаем размер ходста для загрузки изображения
            cw, ch = BOUNDS_OF_CANVAS

            if iw/cw < ih/ch:  # Если соотношение длин меньше соотношения ширин - масштабируем к длине
                pixmap = pixmap.scaledToWidth(cw)
                hoff = (pixmap.height() - ch) // 2
                pixmap = pixmap.copy(
                    QRect(QPoint(0, hoff), QPoint(cw, pixmap.height()-hoff))
                )

            elif iw/cw > ih/ch:  # Иначе - масштабируем к ширине
                pixmap = pixmap.scaledToHeight(ch)
                woff = (pixmap.width() - cw) // 2
                pixmap = pixmap.copy(
                    QRect(QPoint(woff, 0), QPoint(pixmap.width()-woff, ch))
                )

            self.canvas.setPixmap(pixmap)

    def file_save(self):
        """
        Сохраняет холст в файл с изображением
        :return:
        """
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "Файл PNG (*.png)")

        if path:
            pixmap = self.canvas.pixmap()
            pixmap.save(path, "PNG" )

    def invert(self):
        img = QImage(self.canvas.pixmap())
        img.invertPixels()
        pixmap = QPixmap()
        pixmap.convertFromImage(img)
        self.canvas.setPixmap(pixmap)

    def flip_horz(self):
        pixmap = self.canvas.pixmap()
        self.canvas.setPixmap(pixmap.transformed(QTransform().scale(-1, 1)))

    def flip_vert(self):
        pixmap = self.canvas.pixmap()
        self.canvas.setPixmap(pixmap.transformed(QTransform().scale(1, -1)))

    def fractal(self):
        dlg = QFractalDialog(self)
        dlg.exec()
        if dlg.result() == 1:
            self.draw_fractal(dlg.fractal())


    def draw_fractal(self, fractal):
        self.canvas.draw_fractal(fractal)

    def init_canvas(self):
        self.horizontalLayout.removeWidget(self.canvas)
        self.canvas = Canvas()
        self.canvas.initialize()
        self.horizontalLayout.addWidget(self.canvas)

    def init_mode_buttons(self):
        # Инициализируем кнопки режимов рисования
        mode_group = QButtonGroup(self)
        mode_group.setExclusive(True)

        for mode in BTN_MODES:
            btn = getattr(self, f'{mode}Button')
            btn.pressed.connect(lambda mode=mode: self.canvas.set_mode(mode))
            mode_group.addButton(btn)

    def init_event_props(self):
        self.canvas.setMouseTracking(True)
        self.canvas.setFocusPolicy(Qt.StrongFocus)

    def init_stamps(self):
        # Инициализация режима штампов
        self.current_stamp_n = -1
        self.next_stamp()
        # заряжаем обработчик событий
        self.stampNextButton.pressed.connect(self.next_stamp)
        
    # def init_clipboard_copy_button(self):
    #     self.actionCopy.triggered.connect(self.copy_to_clipboard)

    # def copy_to_clipboard(self):
    #     clipboard = QApplication.clipboard()

    #     if self.canvas.mode == 'selectRectangular' and self.canvas.locked:
    #         clipboard.setPixmap(self.canvas.selectRectangular_copy())

    #     elif self.canvas.mode == 'selectPolygon' and self.canvas.locked:
    #         clipboard.setPixmap(self.canvas.selectPolygon_copy())

    #     else:
    #         clipboard.setPixmap(self.canvas.pixmap())

    def init_colors(self):
        for index, color in enumerate(PICK_COLORS, 1):
            btn = getattr(self, 'colorButton_%d' % index)
            btn.setStyleSheet('QPushButton { background-color: %s; }' % color)
            btn.hex = color  

    # def init_languages(self):
        # self.load_language_files()

        # self.translator = QTranslator(self)
        # locale = Locale.default()
        # self.set_current_language(locale)

    def init_color_selection(self):
        # Инициализируем кнопки выбора цвета
        self.primaryColorButton.pressed.connect(lambda: self.choose_color(self.set_primary_color))
        self.secondaryColorButton.pressed.connect(lambda: self.choose_color(self.set_secondary_color))

        self.set_primary_color('#000000')
        self.set_secondary_color('#ffffff')

        # Подключаем обработчики нажатий на кнопки для кнопок с выбором цветов
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

    def next_stamp(self):
        self.current_stamp_n += 1
        if self.current_stamp_n >= len(STAMPS):
            self.current_stamp_n = 0

        pixmap = QPixmap(STAMPS[self.current_stamp_n])
        self.stampNextButton.setIcon(QIcon(pixmap))

        self.canvas.current_stamp = pixmap

    # def load_current_language(self, fn):
    #     app = QApplication.instance()
    #     if os.path.isfile(fn):
    #         if self.translator.load(fn):
    #           app.installTranslator(self.translator)
    #     else:
    #         app.removeTranslator(self.translator)
    #     self.retranslateUi(self)
        
    # def set_current_language(self, locale):
    #     lang_path = os.path.join(self.get_lang_dir(),f'{locale.language}-{locale.territory}.qm')
    #     self.load_current_language(lang_path)

    # def select_lang_func(self, tr):
    #     sender = self.sender()
    #     self.load_current_language(sender.data())
   

    # def add_lang_menu(self, ln, fn):
    #     langAct = QAction(ln, self)
    #     langAct.setData(fn)
    #     langAct.triggered.connect(self.select_lang_func)
    #     self.menuLanguage.addAction(langAct)

    # def get_lang_dir(self):
    #     return os.path.join(os.path.dirname(__file__),'resources/lang')

    # def load_language_files(self):
    #     lang_dir = self.get_lang_dir()
    #     for file in os.listdir(lang_dir):
    #         fn = os.fsdecode(file)
    #         if fn.endswith('.qm'):
    #             ll = fn[:-3]
    #             lp = ll.split('-')
    #             ln = Locale(lp[0], lp[1])
    #             self.add_lang_menu(ln.display_name, os.path.join(lang_dir,fn))

    # def retranslateUi(self, wnd):
    #     _translate = QCoreApplication.translate
    #     wnd.setWindowTitle(_translate("PainWindow", "Pain"))
    #     self.menuFile.setTitle(_translate("PainWindow", "File"))
    #     self.menuEdit.setTitle(_translate("PainWindow", "Edit"))
    #     self.menuImage.setTitle(_translate("PainWindow", "Image"))
    #     self.menuTools.setTitle(_translate("PainWindow", "Tools"))
    #     # self.menuLanguage.setTitle(_translate("PainWindow", "Language..."))
    #     self.menuHelp.setTitle(_translate("PainWindow", "Help"))
    #     self.fileToolbar.setWindowTitle(_translate("PainWindow", "toolBar"))
    #     self.drawingToolbar.setWindowTitle(_translate("PainWindow", "toolBar"))
    #     self.fontToolbar.setWindowTitle(_translate("PainWindow", "toolBar"))
    #     # self.actionCopy.setText(_translate("PainWindow", "Copy"))
    #     # self.actionCopy.setShortcut(_translate("PainWindow", "Ctrl+C"))
    #     self.actionClearImage.setText(_translate("PainWindow", "Clear Image"))
    #     self.actionOpenImage.setText(_translate("PainWindow", "Open Image..."))
    #     self.actionSaveImage.setText(_translate("PainWindow", "Save Image As..."))
    #     self.actionInvertColors.setText(_translate("PainWindow", "Invert Colors"))
    #     self.actionFlipHorizontal.setText(_translate("PainWindow", "Flip Horizontal"))
    #     self.actionFlipVertical.setText(_translate("PainWindow", "Flip Vertical"))
    #     self.actionFlipVertical.setText(_translate("PainWindow", "Fractal"))
    #     self.actionNewImage.setText(_translate("PainWindow", "New Image"))
    #     self.actionBold.setText(_translate("PainWindow", "Bold"))
    #     self.actionBold.setShortcut(_translate("PainWindow", "Ctrl+B"))
    #     self.actionItalic.setText(_translate("PainWindow", "Italic"))
    #     self.actionItalic.setShortcut(_translate("PainWindow", "Ctrl+I"))
    #     self.actionUnderline.setText(_translate("PainWindow", "Underline"))
    #     self.actionFillShapes.setText(_translate("PainWindow", "Fill Shapes?"))
    

        