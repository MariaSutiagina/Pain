# Проект PyQt5 «Графический дизайнер "Pain"»

## 1. Задачи проекта

Создать приложение - графический дизайнер.

Приложение должно иметь следующие функции:

1. Файл должен открываться в формате jpg; png
2. Файл должен быть сохранен в формате jpg; png
3. Программа должна быть написана на python qt5
4. Программа должна работать под операционной системой Windows; Linux
5. Программа должна позволять создавать четырехугольники произвольного размера, с выбранным цветом и толщиной линии 
6. Программа должна позволять создавать окружности произвольного размера, с выбранным цветом и толщиной линии 
7. Программа должна позволять создавать линии произвольного размера, с выбранным цветом и толщиной линии 
8. Программа должна позволять создавать закругленные четырехугольники произвольного размера, с выбранным цветом и толщиной линии 
9. Программа должна позволять создавать ломаные линии произвольного размера, с выбранным цветом и выбранной толщиной линии
10. Программа должна позволять создавать многоугольники произвольного размера, с выбранным цветом и толщиной линии 
11. Программа должна позволять создавать текст произвольного размера, с выбранным цветом и шрифтом
12. Программа должна позволять выбрать инструмент баллончик, с регулируемым размером и выбранным цветом
13. Программа должна позволять выбрать инструмент кисть, с регулируемым размером и выбранным цветом
14. Программа должна позволять выбрать инструмент  карандаш, с регулируемым размером и выбранным цветом
15. Программа должна позволять выбрать инструмент ластик с регулируемым размером
16. Программа должна позволять использовать цвет уже находящийся на экране с помощью инструмента пипетка
17. Программа должна позволять выбрать инструмент заливку с выбранным цветом
18. Программа должна позволять добавлять стикеры на экран, с помощью инструмента штамп
19. Программа должна позволять выделять текст жирным шрифтом, с помощью кнопки «жирный»
20. Программа должна позволять выделять текст курсивом, с помощью кнопки «курсив»
21. Программа должна позволять подчеркивать текст, с помощью кнопки «подчеркивание»

## 2. Установка и запуск приложения

Приложение протестировано для Python версии 3.8.
Для установки зависимостей приложения создайте новое виртуальное окружение Python 3, активируйте его и выполните команду

```
pip install -r requirements.txt
```

После этого приложение можно будет запустить командой
```
python3 qtpain.py
```

## 3. Работа с приложением

Основная работа с приложением производится через главное окно, имеющее  меню и три основных панели с инструментами в графическом дизайнере.
![Пользовательский интерфейс]("https://github.com/MariaSutiagina/Pain/blob/main/docs/images/%D0%B8%D0%BD%D1%82%D0%B5%D1%80%D1%84%D0%B5%D0%B9%D1%81.png" "Пользовательский интерфейс")

## 3.1 Панель №1

На верхней панели, распологаються такие инструменты, как: "new image" - позволяет создать новый файл; "open image" - позволяет открыть готовый файл; "save image as" - позволяет сохранить файл; ползунок, позволяющий регулировать размер линии; инструмент позволяющий выбрать шрифт печатного текста; инструмент, позволяющий выбрать размер печатного текста; "жирный" - позволяет выделить печатный текст, жирным; "курсив" - позволяет выделить печатный текст, курсивом; "подчеркивание" - позволяет подчеркнуть печатный текст

## 3.1 Панель №2

На левой панели, распологаются такие инструменты, как: кисть - "ластик", позволяющая стирать нарисованое; инструмент - "заливка", позволяющий залить одним цветом всё пространство; инструмент - "пипетка", позволяющющий скопировать уже использованый цвет; инструмент - "штамп", позволяющий поставить опеределенный рисунок в любую часть листа; кисть - "карандаш", позволяющая рисовать; кисть - "кисточка", позволяющая рисовать; кисть - "баллончик", позволяющая рисовать; инструмент - "текст"Б позволяющий создать печатный текст; инструмент - "луч", позволяющий нарисовать прямую линию произвольного размера; инструмент - "кривая", позволяющий нарисовать кривую произвольного размера; инструмент - "четырехугольник", позволяющий нарисовать четырехугольник произвольного размера; инструмент - "многоугольник", позволяющий нарисовать многоугольник произвольного размера; инструмент - "овал", позволяющий нарисовать овал произвольного размера; инструмент - "скругленный четырехугольник", позволяющий нарисовать скругленный четырехугольник произвольного размера; 

 ## 3.1 Панель №3

На нижней панели, распологаеться палитра членов и кнопка для выбора штампа

## 3.1 Меню

В меню имеются три вкладки. с помощью первой вкладки, возможно создать новый файл, открыть готовый или сохранить открытый; с помощью второй, возможно отчистить всё нарисованое; с помощью третьей, можно инвертировать цвета на изображении, повернуть по вертикали или горизонтали


