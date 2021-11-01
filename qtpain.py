from PyQt5.QtWidgets import QApplication
from PyQt5 import QtGui
from PainWindow import QPainWindow

import sys
import resources

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QPainWindow()
    app.exec_()