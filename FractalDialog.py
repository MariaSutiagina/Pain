from PyQt5 import uic
from PyQt5.QtWidgets import QDialog
from fractal import Fractal
import utils
class QFractalDialog(QDialog):
    def __init__(self, parent=None):
        super(QFractalDialog, self).__init__(parent)
        uic.loadUi(utils.resource_path('resources/fractal_settings.ui'), self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def fractal(self):
        f = Fractal(self.cbType.currentIndex(), 1-int(self.rbLeft.isChecked()))
        f.limit = self.slSteps.value()
        f.color = 'rgb'[self.cbColor.currentIndex()]
        return f
