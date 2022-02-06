from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal
from PyQt5 import uic
import os

class Custom_Widget(QWidget):
    # сигнал для кнопки удаления
    delete = pyqtSignal()
    # сигнал для открытия окна с текстом
    open = pyqtSignal()
    # сигнал для переноса в любимые
    fav = pyqtSignal()
    # сигнал для перенеоса в 'хочу прочитать'
    want_to = pyqtSignal()
    # сигнал для перенеоса в прочитанные
    reade = pyqtSignal()
    # сигнал для перенеоса на домашнюю страницу
    home = pyqtSignal()

    def __init__(self, filename: str):
        super(Custom_Widget, self).__init__()
        uic.loadUi("books.ui", self)
        self.filename = filename
        self.nazv_2.setText(f"      {os.path.basename(f'{filename}')}")
        self.nazv_2.setStyleSheet('''font-family: Times New Roman;
                                    font-size: 30px;''')
        self.delete_2.clicked.connect(self.delete)
        self.to_windowforread.clicked.connect(self.open)
        self.to_fav.clicked.connect(self.fav)
        self.to_want_to_read.clicked.connect(self.want_to)
        self.read.clicked.connect(self.reade)
        self.to_home.clicked.connect(self.home)