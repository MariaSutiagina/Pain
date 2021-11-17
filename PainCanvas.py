from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QColor, QPixmap, QPen, QPainter, QPolygon, QBitmap, QBrush, QFont
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QPoint

import random

CANVAS_SIZE = 600, 400
SELECTION_LINE_PATTERN = QPen(QColor(0xff, 0xff, 0xff), 1, Qt.DashLine)
LINE_PATTERN = QPen(QColor(0xff, 0xff, 0xff), 1, Qt.SolidLine)

BRUSH_SIZE_FACTOR = 3
SPRAY_SIZE_FACTOR = 5
SPRAY_DOTS_COUNT = 100

def construct_font(options):
    """
    Создает фонт из значений, заданных в опциях
    :param options:
    :return: QFont
    """
    font = options['font']
    font.setPointSize(options['fontsize'])
    font.setBold(options['bold'])
    font.setItalic(options['italic'])
    font.setUnderline(options['underline'])
    return font

class Canvas(QLabel):

    mode = 'rectangle'
    secondary_color = None

    timer_event = None

    primary_color_updated = pyqtSignal(str)
    secondary_color_updated = pyqtSignal(str)

    current_stamp = None

    # Хранит настройки режимов
    options = {
        # Настройки рисования
        'size': 1,
        'fill': True,
        # Настройки шрифтов
        'font': QFont('Times'),
        'fontsize': 12,
        'bold': False,
        'italic': False,
        'underline': False,
    }

    
    def initialize(self):
        if self.secondary_color:
            self.background_color = QColor(self.secondary_color)  
            self.eraser_color = QColor(self.secondary_color)
        else:
            self.background_color = QColor(Qt.white)
            self.eraser_color = QColor(Qt.white)


        self.eraser_color.setAlpha(100)
        self.reset()
        self.set_mode("")

    def reset(self):
        # создаем растр на холсте
        self.setPixmap(QPixmap(*CANVAS_SIZE))
        # стираем все на холсте
        self.pixmap().fill(self.background_color)


    def set_primary_color(self, hex):
        self.primary_color = QColor(hex)

    def set_secondary_color(self, hex):
        self.secondary_color = QColor(hex)

    def set_options(self, key, value):
        self.options[key] = value

    def set_options(self, key, value):
        self.options[key] = value

    def set_mode(self, mode):
        # инициализируем атрибуты при смене режима
        # Останавливаем таймер анимации 
        self.timer_cleanup()
        # if self.mode.startswith('select') and self.mode != mode:
        #     self.reset_selection()

        self.active_shape_fn = None
        self.active_shape_args = ()

        self.origin_pos = None
        self.current_pos = None
        self.last_pos = None
        self.history_pos = None
        self.last_history = []
        # self.last_selection = {}

        self.current_text = ""
        self.last_text = ""

        self.last_options = {}

        self.dash_offset = 0
        self.locked = False

        # Установим новый режим
        self.mode = mode

    def resize(self, size):
        cw = self.width()
        ch = self.height()

        pixmap = QPixmap(cw, ch)
        pixmap.fill(self.background_color)

        pm = self.pixmap()
        p = QPainter(pixmap)
        p.drawPixmap(0,0, pm)
        self.setPixmap(pixmap)
        p.end()
        self.update()




    def reset_mode(self):
        # Сброс настроек режима
        self.set_mode(self.mode)

    # сброс таймера
    def timer_cleanup(self):
        # если есть специфический для режима обработчик - запускаем его с флагом "последний раз"
        if self.timer_event:
            # останавливаем таймер
            timer_event = self.timer_event
            self.timer_event = None
            timer_event(final=True)

    # обработчик события от таймера
    def on_timer(self):
        # если определен специфический обработчик - запускаем его
        if self.timer_event:
            self.timer_event()

    # обработчики события от мыши, 
    # которые зависят от текущего режима
    # нажатие на кнопку
    def mousePressEvent(self, e):
        # если определен обработчик - запускаем его
        fn = getattr(self, "%s_mousePressEvent" % self.mode, None)
        if fn:
            return fn(e)

    # на перемещение
    def mouseMoveEvent(self, e):
        # если есть обработчик - запускаем его
        fn = getattr(self, "%s_mouseMoveEvent" % self.mode, None)
        if fn:
            return fn(e)

    # отпускание кнопки
    def mouseReleaseEvent(self, e):
        # если есть обработчик - запускаем его
        fn = getattr(self, "%s_mouseReleaseEvent" % self.mode, None)
        if fn:
            return fn(e)

    # двойной клик
    def mouseDoubleClickEvent(self, e):
        # если есть обработчик - запускаем его
        fn = getattr(self, "%s_mouseDoubleClickEvent" % self.mode, None)
        if fn:
            return fn(e)

    # первоначальные обработчики мыши для любого режима - 
    # левая кнопка - первый цвет, правая - второй
    # + - запоминаем позицию мыши
    def primary_mousePressEvent(self, e):
        self.last_pos = e.pos()

        if e.button() == Qt.LeftButton:
            self.active_color = self.primary_color
        else:
            self.active_color = self.secondary_color
    
    # забываем позицию мыши при отпускании кнопки
    def primary_mouseReleaseEvent(self, e):
        self.last_pos = None


    # Первичные обработчики для режимов, связанных с многоугольниками
    def primary_polygon_mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self.history_pos:
                self.history_pos.append(e.pos())
            else:
                self.timer_event = self.primary_polygon_timerEvent
                self.current_pos = e.pos()
                self.history_pos = [e.pos()]

        elif e.button() == Qt.RightButton and self.history_pos:
            # Делаем ресет режима
            self.timer_cleanup()
            self.reset_mode()

    # обработчик тика таймера для режима многоугольника
    def primary_polygon_timerEvent(self, final=False):

        p = QPainter(self.pixmap())
        p.setCompositionMode(QPainter.RasterOp_SourceXorDestination)
        pen = self.preview_pen
        pen.setDashOffset(self.dash_offset)
        p.setPen(pen)
        if self.last_history:
            getattr(p, self.active_shape_fn)(*self.last_history)

        if not final:
            self.dash_offset -= 1
            pen.setDashOffset(self.dash_offset)
            p.setPen(pen)
            getattr(p, self.active_shape_fn)(*self.history_pos + [self.current_pos])

        self.update()
        self.last_pos = self.current_pos
        self.last_history = self.history_pos + [self.current_pos]

    def primary_polygon_mouseMoveEvent(self, e):
        self.current_pos = e.pos()

    def primary_polygon_mouseDoubleClickEvent(self, e):
        self.timer_cleanup()
        p = QPainter(self.pixmap())
        p.setPen(QPen(self.primary_color, self.options['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        if self.secondary_color:
            p.setBrush(QBrush(self.secondary_color))

        getattr(p, self.active_shape_fn)(*self.history_pos + [e.pos()])
        self.update()
        self.reset_mode()

    # первичные обработчики для фигур

    def primary_shape_mousePressEvent(self, e):
        # if self.mode in self.last_selection:
        self.timer_cleanup()
            # self.reset_selection()

        self.origin_pos = e.pos()
        self.current_pos = e.pos()
        self.timer_event = self.primary_shape_timerEvent

    def primary_shape_timerEvent(self, final=False):
        p = QPainter(self.pixmap())
        p.setCompositionMode(QPainter.RasterOp_SourceXorDestination)
        pen = self.preview_pen
        pen.setDashOffset(self.dash_offset)
        p.setPen(pen)
        if self.last_pos:
            r = QRect(self.origin_pos, self.last_pos)
            params = [r, self.dash_offset]
            if r is not None and not (r.width()==1 and r.height()==1):
                getattr(p, self.active_shape_fn)(r, *self.active_shape_args)                

                if not final:
                    self.dash_offset -= 1
                    params.append(self.dash_offset)
                    pen.setDashOffset(self.dash_offset)
                    p.setPen(pen)
                    getattr(p, self.active_shape_fn)(r, *self.active_shape_args)
            
                # if r is not None and not (r.width()==1 and r.height()==1):
                #     self.last_selection[self.mode] = params
            
        self.update()
        self.last_pos = self.current_pos

    # def reset_selection(self):
    #     if self.mode in self.last_selection:
    #         p = QPainter(self.pixmap())
    #         p.setCompositionMode(QPainter.RasterOp_SourceXorDestination)
    #         pen = self.preview_pen
    #         params = self.last_selection[self.mode]

    #         pen.setDashOffset(params[1])
    #         p.setPen(pen)
    #         getattr(p, self.active_shape_fn)(params[0], *self.active_shape_args)
                
    #         if len(params) > 2:
    #             pen.setDashOffset(params[2])
    #             p.setPen(pen)
    #             getattr(p, self.active_shape_fn)(params[0], *self.active_shape_args)

    #         self.last_selection[self.mode] = None
            
    #         self.update()

    #     self.last_pos = self.current_pos

    def primary_shape_mouseMoveEvent(self, e):
        self.current_pos = e.pos()

    def primary_shape_mouseReleaseEvent(self, e):
        if self.last_pos:
            self.timer_cleanup()

            p = QPainter(self.pixmap())
            p.setPen(QPen(self.primary_color, self.options['size'], Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))

            if self.options['fill']:
                p.setBrush(QBrush(self.secondary_color))
            getattr(p, self.active_shape_fn)(QRect(self.origin_pos, e.pos()), *self.active_shape_args)
            self.update()

        self.reset_mode()

    # Обработчики, которые зависят от режима

    # режим "выделение многоугольника"
    # def selectPolygon_mousePressEvent(self, e):
    #     if not self.locked or e.button == Qt.RightButton:
    #         self.active_shape_fn = 'drawPolygon'
    #         self.preview_pen = SELECTION_LINE_PATTERN
    #         self.primary_polygon_mousePressEvent(e)

    # def selectPolygon_timerEvent(self, final=False):
    #     self.primary_polygon_timerEvent(final)

    # def selectPolygon_mouseMoveEvent(self, e):
    #     if not self.locked:
    #         self.primary_polygon_mouseMoveEvent(e)

    # def selectPolygon_mouseDoubleClickEvent(self, e):
    #     self.locked = True
    #     self.current_pos = e.pos()

    # def selectPolygon_copy(self):
    #     """ Копирует многоугольную область холста и возвращает ее копию
    #     :return: объект QPixmapс копией выделенной области.
    #     """
    #     self.timer_cleanup()

    #     pixmap = self.pixmap().copy()
    #     bitmap = QBitmap(*CANVAS_SIZE) # создает bitmap по размеру холста
    #     bitmap.clear()  # очищает его, т.к. там бывает мусор

    #     p = QPainter(bitmap)
    #     # Создаем маску с выделенным многоугольником,
    #     # звкрашенную цветом 000001, остальная часть маски - прозрачная
    #     userpoly = QPolygon(self.history_pos + [self.current_pos])
    #     p.setPen(QPen(Qt.color1))
    #     p.setBrush(QBrush(Qt.color1))  # Solid color, Qt.color1 == bit on.
    #     p.drawPolygon(userpoly)
    #     p.end()

    #     # Учтанавливаем маску на копию холста
    #     pixmap.setMask(bitmap)

    #     # копируем и возвращаеем копию прямоугольного участка холста, в который вписан выделенный многоугольник
    #     return pixmap.copy(userpoly.boundingRect())

    # Выделение прямоугольной области
    # def selectRectangular_mousePressEvent(self, e):
    #     self.active_shape_fn = 'drawRect'
    #     self.preview_pen = SELECTION_LINE_PATTERN
    #     self.primary_shape_mousePressEvent(e)

    # def selectRectangular_timerEvent(self, final=False):
    #     self.primary_shape_timerEvent(final)

    # def selectRectangular_mouseMoveEvent(self, e):
    #     if not self.locked:
    #         self.current_pos = e.pos()

    # def selectRectangular_mouseReleaseEvent(self, e):
    #     self.current_pos = e.pos()
    #     self.locked = True

    # def selectRectangular_copy(self):
    #     """
    #     Копируем прямоугольную область изображения и возвращаем ее

    #     :return: объект QPixmap с копией прямоугольной области
    #     """
    #     if self.mode in self.last_selection:
    #         self.timer_cleanup()
    #         return self.pixmap().copy(self.last_selection[self.mode][0])


    # Обработчики мыши в режиме рисования линий
    def pen_mousePressEvent(self, e):
        self.primary_mousePressEvent(e)

    def pen_mouseMoveEvent(self, e):
        if self.last_pos:
            p = QPainter(self.pixmap())
            p.setPen(QPen(self.active_color, self.options['size'], Qt.SolidLine, Qt.SquareCap, Qt.RoundJoin))
            p.drawLine(self.last_pos, e.pos())

            self.last_pos = e.pos()
            self.update()

    def pen_mouseReleaseEvent(self, e):
        self.primary_mouseReleaseEvent(e)

    # Обработчики мыши в режиме стирания
    def eraser_mousePressEvent(self, e):
        self.primary_mousePressEvent(e)

    def eraser_mouseMoveEvent(self, e):
        if self.last_pos:
            p = QPainter(self.pixmap())
            p.setPen(QPen(self.eraser_color, 30, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawLine(self.last_pos, e.pos())

            self.last_pos = e.pos()
            self.update()

    def eraser_mouseReleaseEvent(self, e):
        self.primary_mouseReleaseEvent(e)


    # Обработчики мыши в режиме "Кисть"

    def brush_mousePressEvent(self, e):
        self.primary_mousePressEvent(e)

    def brush_mouseMoveEvent(self, e):
        if self.last_pos:
            p = QPainter(self.pixmap())
            p.setPen(QPen(self.active_color, self.options['size'] * BRUSH_SIZE_FACTOR, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawLine(self.last_pos, e.pos())

            self.last_pos = e.pos()
            self.update()

    def brush_mouseReleaseEvent(self, e):
        self.primary_mouseReleaseEvent(e)

    # Обработчики мыши в режиме "Спрей"

    def spray_mousePressEvent(self, e):
        self.primary_mousePressEvent(e)

    def spray_mouseMoveEvent(self, e):
        if self.last_pos:
            p = QPainter(self.pixmap())
            p.setPen(QPen(self.active_color, 1))

            for n in range(self.options['size'] * SPRAY_DOTS_COUNT):
                xo = random.gauss(0, self.options['size'] * SPRAY_SIZE_FACTOR)
                yo = random.gauss(0, self.options['size'] * SPRAY_SIZE_FACTOR)
                p.drawPoint(e.x() + xo, e.y() + yo)

        self.update()

    def spray_mouseReleaseEvent(self, e):
        self.primary_mouseReleaseEvent(e)

    # Обработчики мыши в режиме заливки

    def fill_mousePressEvent(self, e):

        if e.button() == Qt.LeftButton:
            self.active_color = self.primary_color
        else:
            self.active_color = self.secondary_color

        image = self.pixmap().toImage()
        w, h = image.width(), image.height()
        x, y = e.x(), e.y()

        # Получаем цвет пикселя с холста
        target_color = image.pixel(x,y)

        have_seen = set()
        queue = [(x, y)]

        def get_adjacent_points(have_seen, center_pos):
            points = []
            cx, cy = center_pos
            # не обрабатываем диагональные точки, 
            # т.к. это повод просочиться сквозь границу заливки
            for x, y in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                x1, y1 = cx + x, cy + y
                if ((x1, y1) not in have_seen and 
                    x1 >= 0 and x1 < w and
                    y1 >= 0 and y1 < h):

                    points.append((x1, y1))
                    have_seen.add((x1, y1))

            return points

        p = QPainter(self.pixmap())
        p.setPen(QPen(self.active_color))

        # Поиск и заливка
        while queue:
            x, y = queue.pop()
            if image.pixel(x, y) == target_color:
                p.drawPoint(QPoint(x, y))
                queue.extend(get_adjacent_points(have_seen, (x, y)))

        self.update()

    # События мыши в режиме рисования отрезков

    def line_mousePressEvent(self, e):
        self.origin_pos = e.pos()
        self.current_pos = e.pos()
        self.preview_pen = LINE_PATTERN
        self.timer_event = self.line_timerEvent

    def line_timerEvent(self, final=False):
        p = QPainter(self.pixmap())
        p.setCompositionMode(QPainter.RasterOp_SourceXorDestination)
        pen = self.preview_pen
        p.setPen(pen)

        # рисуем макет линии
        if self.last_pos:
            p.drawLine(self.origin_pos, self.last_pos)

        if not final:
            p.drawLine(self.origin_pos, self.current_pos)

        self.update()
        self.last_pos = self.current_pos

    def line_mouseMoveEvent(self, e):
        self.current_pos = e.pos()

    def line_mouseReleaseEvent(self, e):
        if self.last_pos:
            # Стереть мекет линии
            self.timer_cleanup()

            p = QPainter(self.pixmap())
            p.setPen(QPen(self.primary_color, self.options['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            # Нарисовать линию
            p.drawLine(self.origin_pos, e.pos())
            self.update()

        self.reset_mode()

    # Обработчики событий в режиме "Пипетка"
    def pipette_mousePressEvent(self, e):
        c = self.pixmap().toImage().pixel(e.pos())
        color = QColor(c).name()

        if e.button() == Qt.LeftButton:
            self.set_primary_color(color)
            self.primary_color_updated.emit(color)  # Запустить событие

        elif e.button() == Qt.RightButton:
            self.set_secondary_color(color)
            self.secondary_color_updated.emit(color)  # Запустить событие

    # обработчики мыши в режиме полилинии

    def polyLine_mousePressEvent(self, e):
        self.active_shape_fn = 'drawPolyline'
        self.preview_pen = SELECTION_LINE_PATTERN
        self.primary_polygon_mousePressEvent(e)

    def polyLine_timerEvent(self, final=False):
        self.primary_polygon_timerEvent(final)

    def polyLine_mouseMoveEvent(self, e):
        self.primary_polygon_mouseMoveEvent(e)

    def polyLine_mouseDoubleClickEvent(self, e):
        self.primary_polygon_mouseDoubleClickEvent(e)

    # обработчики мыши в режиме рисоания прямоугольников

    def rectangle_mousePressEvent(self, e):
        self.active_shape_fn = 'drawRect'
        self.active_shape_args = ()
        self.preview_pen = SELECTION_LINE_PATTERN
        self.primary_shape_mousePressEvent(e)

    def rectangle_timerEvent(self, final=False):
        self.primary_shape_timerEvent(final)

    def rect_mouseMoveEvent(self, e):
        self.primary_shape_mouseMoveEvent(e)

    def rectangle_mouseReleaseEvent(self, e):
        self.primary_shape_mouseReleaseEvent(e)

    # обработчики мыши в режиме рисоания многоугольников

    def polygon_mousePressEvent(self, e):
        self.active_shape_fn = 'drawPolygon'
        self.preview_pen = SELECTION_LINE_PATTERN
        self.primary_polygon_mousePressEvent(e)

    def polygon_timerEvent(self, final=False):
        self.primary_polygon_timerEvent(final)

    def polygon_mouseMoveEvent(self, e):
        self.primary_polygon_mouseMoveEvent(e)

    def polygon_mouseDoubleClickEvent(self, e):
        self.primary_polygon_mouseDoubleClickEvent(e)

    # обработчики мыши в режиме рисоания эллипсов

    def ellipse_mousePressEvent(self, e):
        self.active_shape_fn = 'drawEllipse'
        self.active_shape_args = ()
        self.preview_pen = SELECTION_LINE_PATTERN
        self.primary_shape_mousePressEvent(e)

    def ellipse_timerEvent(self, final=False):
        self.primary_shape_timerEvent(final)

    def ellipse_mouseMoveEvent(self, e):
        self.primary_shape_mouseMoveEvent(e)

    def ellipse_mouseReleaseEvent(self, e):
        self.primary_shape_mouseReleaseEvent(e)

    # обработчики мыши в режиме рисоания овалов

    def roundRectangle_mousePressEvent(self, e):
        self.active_shape_fn = 'drawRoundedRect'
        self.active_shape_args = (25, 25)
        self.preview_pen = SELECTION_LINE_PATTERN
        self.primary_shape_mousePressEvent(e)

    def roundRectangle_timerEvent(self, final=False):
        self.primary_shape_timerEvent(final)

    def roundRectangle_mouseMoveEvent(self, e):
        self.primary_shape_mouseMoveEvent(e)

    def roundRectangle_mouseReleaseEvent(self, e):
        self.primary_shape_mouseReleaseEvent(e)

    def stamp_mousePressEvent(self, e):
        p = QPainter(self.pixmap())
        stamp = self.current_stamp
        p.drawPixmap(e.x() - stamp.width() // 2, e.y() - stamp.height() // 2, stamp)
        self.update()

    # Обработчики событий от мыши и клавиатуры в режиме текста

    def keyPressEvent(self, e):
        if self.mode == 'text':
            if e.key() == Qt.Key_Backspace:
                self.current_text = self.current_text[:-1]
            else:
                self.current_text = self.current_text + e.text()

    def text_mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and self.current_pos is None:
            self.current_pos = e.pos()
            self.current_text = ""
            self.timer_event = self.text_timerEvent

        elif e.button() == Qt.LeftButton:

            self.timer_cleanup()
            # Рисуем текст
            p = QPainter(self.pixmap())
            p.setRenderHints(QPainter.Antialiasing)
            font = construct_font(self.options)
            p.setFont(font)
            pen = QPen(self.primary_color, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            p.setPen(pen)
            p.drawText(self.current_pos, self.current_text)
            self.update()

            self.reset_mode()

        elif e.button() == Qt.RightButton and self.current_pos:
            self.reset_mode()

    def text_timerEvent(self, final=False):
        p = QPainter(self.pixmap())
        p.setCompositionMode(QPainter.RasterOp_SourceXorDestination)
        pen = SELECTION_LINE_PATTERN
        p.setPen(pen)
        if self.last_text:
            font = construct_font(self.last_options)
            p.setFont(font)
            p.drawText(self.current_pos, self.last_text)

        if not final:
            font = construct_font(self.options)
            p.setFont(font)
            p.drawText(self.current_pos, self.current_text)

        self.last_text = self.current_text
        self.last_options = self.options.copy()
        self.update()



