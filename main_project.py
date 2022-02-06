import io
import sys
import sqlite3
from PyQt5 import uic, QtGui  # Импортируем uic
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QListWidgetItem, QFileDialog, QAbstractItemView, QMessageBox
import os
import logo
from custom_widget import Custom_Widget
from PyQt5.QtCore import QXmlStreamReader, QByteArray, QXmlStreamWriter, Qt
from zipfile import ZipFile


# основное окно
class MyWidget(QMainWindow):
    def __init__(self):
        super(MyWidget, self).__init__()
        uic.loadUi("design.ui", self)
        self.initUi()
        self.con = sqlite3.connect("BaseOfBooks.db")
        self.my_id_counter = 1
        self.data = {"homeList": [],
                     "favList": [],
                     "want_to_readList": [],
                     "readList": []}
        self.tags = {'poem': 'i', 'emphasis': 'i', 'stanza': 'i', 'title': 'p', 'empty-line': 'br',
                     'subtitle': 'p', 'section': 'p', 'strong': 'b', 'v': 'p', 'coverpage': 'br', }
        self.attrs = {
            'title': {'align': 'center', 'style': 'font-size:24px;'},
            'subtitle': {'align': 'center', 'style': 'font-size:22px;'},
            'table': {'width': '100%', 'align': 'center', 'border': '1'},
            'td': {'align': 'center'},
            'p': {'align': 'justify', 'style': 'font-size:20px;'}, }
        self.my_widgets_List_dict: dict[str, QListWidgetItem] = {}
        self.lists = {"homeList": self.homeList,
                      "favList": self.favList,
                      "want_to_readList": self.want_to_readList,
                      "readList": self.readList}
        self.from_db_home()
        self.from_db_fav()
        self.from_db_want_to()
        self.from_db_read()

    def initUi(self):
        self.btn_home.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(0))  # перелистываем на домашнюю страницу
        self.btn_want_to_read.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(2))  # перелистываем на страницу недавние
        self.btn_fav.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(1))  # перелистываем на домашнюю страницу любимое
        self.btn_read.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(3))
        self.btn_exit.clicked.connect(self.exitMethod)
        self.btn_load.clicked.connect(self.dobavlenieMethod)
        self.btn_clear.clicked.connect(self.clear)
        self.homeList.setDragDropMode(QAbstractItemView.InternalMove)  # перетасктваем виджеты
        self.favList.setDragDropMode(QAbstractItemView.InternalMove)  # перетасктваем виджеты
        self.want_to_readList.setDragDropMode(QAbstractItemView.InternalMove)  # перетасктваем виджеты
        self.readList.setDragDropMode(QAbstractItemView.InternalMove)  # перетасктваем виджеты

    # cоздем виджет, который отображает книгу из базы данных в разделе домашняя страница
    def from_db_home(self):
        cur = self.con.cursor()
        ssilka_home = cur.execute("""SELECT ssilka from list_of_books WHERE razdel = 'homeList'""").fetchall()
        for title in ssilka_home:
            self.data['homeList'].append("".join(title))
        for ways in self.data['homeList']:
            self.add_Widget(ways)
            self.my_id_counter += 1

    # cоздем виджет, который отображает книгу из базы данных в разделе любимые
    def from_db_fav(self):
        cur = self.con.cursor()
        ssilka_fav = cur.execute("""SELECT ssilka from list_of_books WHERE razdel = 'favList'""").fetchall()
        for title in ssilka_fav:
            self.data['favList'].append("".join(title))
        for ways in self.data['favList']:
            self.add_Widget_fav(ways)
            self.my_id_counter += 1

    # cоздем виджет, который отображает книгу из базы данных в разделе хочу прочитать
    def from_db_want_to(self):
        cur = self.con.cursor()
        ssilka_want_to = cur.execute(
            """SELECT ssilka from list_of_books WHERE razdel = 'want_to_readList'""").fetchall()
        for title in ssilka_want_to:
            self.data['want_to_readList'].append("".join(title))
        for ways in self.data['want_to_readList']:
            self.add_Widget_want_to(ways)
            self.my_id_counter += 1

    # cоздем виджет, который отображает книгу из базы данных в разделе прочитанные
    def from_db_read(self):
        cur = self.con.cursor()
        ssilka_read = cur.execute("""SELECT DISTINCT ssilka from list_of_books WHERE razdel = 'readList'""").fetchall()
        for title in ssilka_read:
            self.data['readList'].append("".join(title))
        for ways in self.data['readList']:
            self.add_Widget_read(ways)
            self.my_id_counter += 1

    # очищает книг и виджетов
    def clear(self):
        self.my_id_counter = 1
        self.data = {"homeList": [],
                     "favList": [],
                     "want_to_readList": [],
                     "readList": []}
        self.homeList.clear()
        self.favList.clear()
        self.want_to_readList.clear()
        self.readList.clear()
        cur = self.con.cursor()
        cur.execute("""DELETE FROM list_of_books""")
        self.con.commit()

    # связывем диалоговое окно с добавлением виджета
    def dobavlenieMethod(self):
        cur = self.con.cursor()
        fname = QFileDialog.getOpenFileName(
            self, 'Выбрать файл для открытия', '',
            'Текстовый файл (*.txt);; fb2 файл (*.fb2);; ZIP файл (*.zip)')[0]
        if fname:
            try:
                self.data['homeList'].append(fname)
                if fname in self.data['favList'] or fname in self.data['want_to_readList'] or fname in self.data[
                    'readList']:
                    del self.data['homeList'][self.data['homeList'].index(fname)]
                    raise Exception
                else:
                    for i in range(len(self.data["homeList"])):
                        if self.data['homeList'].count(self.data['homeList'][i]) > 1:
                            del self.data['homeList'][i]
                            raise Exception
                    self.add_Widget(fname)
                    cur.execute(f"INSERT INTO list_of_books VALUES(?, ?, ?, ?)",
                                (self.my_id_counter, str(os.path.basename(f"{fname}")), "homeList", str(fname)))
                    self.con.commit()
                    self.my_id_counter += 1
            except Exception:
                QMessageBox.critical(self, "Ошибка ", "Выберите другой элемент", QMessageBox.Ok)
            except FileNotFoundError:
                print("Ошибка")

    # выходим из основного окна
    def exitMethod(self):
        QApplication.instance().quit()
        self.con.close()

    # открываем окно для чтения
    def readMethod(self):
        self.reader = Reader()
        self.reader.show()
        widget = self.sender().filename
        self.reader.textBrowser.setFont(QFont("Times", 20))
        if "txt" in widget:  # для открытия txt файлов
            with io.open(widget, "r") as strings:
                self.reader.textBrowser.setText(strings.read())
        if "fb2" in widget:  # для fb2
            with io.open(widget, "rb") as f:
                f = f.read()
                read = self.readFB2(f)
                self.reader.textBrowser.setHtml(read)
        if "zip" in widget:  # для fb2
            with ZipFile(widget) as myzip:
                for i in myzip.namelist():
                    if i.endswith('.fb2'):
                        self.z = i
                with myzip.open(self.z, "r") as f:
                    f = f.read()
                    read = self.readFB2(f)
                    self.reader.textBrowser.setHtml(read)

    # парсер для чтения fb2 файлов
    def readFB2(self, fbdata):
        xmlread = QXmlStreamReader(fbdata)  # Создаем поток чтения, который читает с fbdata
        by = QByteArray()  # делаем  массив байт.
        writer = QXmlStreamWriter(by)  # QXmlStreamWriter нужен для хранения сформированного документа в XML
        writer.setAutoFormatting(True)
        writer.setAutoFormattingIndent(1)
        tokens = []  # Для контроля структуры документа будем хранить список всех открытых тэгов в объекте
        name = ''  # нынешний открытый тег
        d = {}  # добавляем метку рисунка
        images = []  # для вставки рисунка
        while not xmlread.atEnd():
            elem = xmlread.readNext()
            if xmlread.hasError():
                err = xmlread.errorString() + ':' + str(xmlread.lineNumber())
                return err
            if elem == QXmlStreamReader.StartDocument:
                writer.writeStartDocument()
            elif elem == QXmlStreamReader.EndDocument:
                writer.writeEndDocument()
            elif elem == QXmlStreamReader.StartElement:
                name = xmlread.name()
                tokens.append(name)
                if 'description' in tokens and name != 'image':
                    continue
                d = {i.name(): i.value() for i in xmlread.attributes()}
                if name == 'image':  # расположение рисунков
                    link = d.get('href')
                    writer.writeStartElement('p')
                    writer.writeAttribute('align', 'center')
                    writer.writeCharacters(link)
                    writer.writeEndElement()
                    continue
                tag = self.tags.get(name, name)
                writer.writeStartElement('', tag)
                attr = self.attrs.get(name)
                if attr:
                    for i in attr:
                        writer.writeAttribute('', i, attr[i])
                else:
                    for i in d:
                        writer.writeAttribute('', i, d[i])
            elif elem == QXmlStreamReader.EndElement:
                tokens.pop()
                writer.writeEndElement()
            elif elem == QXmlStreamReader.Characters:  # если есть текст в блоке
                if 'description' in tokens:  # описание книги
                    continue  # не выводим
                text = xmlread.text()
                if name == 'binary':  # для рисунков
                    link, typ = d.get('id'), d.get('content-type')
                    content = '<img src=\"data:' + typ + ';base64,' + text + '\"/>'
                    images.append(('#' + link, content,))
                else:
                    writer.writeCharacters(text)
        s = bytes(by).decode()
        for i in images:
            s = s.replace(i[0], i[1])
        del images
        return s

    # добавляем виджеты по умолчанию на вкладку домой
    def add_Widget(self, name):
        widget = Custom_Widget(name)
        my_item = QListWidgetItem(self.homeList)
        self.homeList.addItem(my_item)
        self.homeList.setItemWidget(my_item, widget)
        self.my_widgets_List_dict[widget.filename] = my_item
        widget.delete.connect(self.delete_widget)
        widget.open.connect(self.readMethod)
        widget.fav.connect(self.pagefav)
        widget.want_to.connect(self.want)
        widget.reade.connect(self.rad)

    # добавляем ранее добавленные виджеты во вкладку любимые
    def add_Widget_fav(self, name):
        widget = Custom_Widget(name)
        my_item = QListWidgetItem(self.favList)
        self.favList.addItem(my_item)
        self.favList.setItemWidget(my_item, widget)
        self.my_widgets_List_dict[widget.filename] = my_item
        widget.delete.connect(self.delete_widget)
        widget.open.connect(self.readMethod)
        widget.home.connect(self.homepage)
        widget.want_to.connect(self.want)
        widget.reade.connect(self.rad)

    # добавляем ранее добавленные виджеты во вкладку хочу прочитать
    def add_Widget_want_to(self, name):
        widget = Custom_Widget(name)
        my_item = QListWidgetItem(self.want_to_readList)
        self.want_to_readList.addItem(my_item)
        self.want_to_readList.setItemWidget(my_item, widget)
        self.my_widgets_List_dict[widget.filename] = my_item
        widget.delete.connect(self.delete_widget)
        widget.open.connect(self.readMethod)
        widget.home.connect(self.homepage)
        widget.fav.connect(self.pagefav)
        widget.reade.connect(self.rad)

    # добавляем ранее добавленные виджеты во вкладку прочитнаные
    def add_Widget_read(self, name):
        widget = Custom_Widget(name)
        my_item = QListWidgetItem(self.readList)
        self.readList.addItem(my_item)
        self.readList.setItemWidget(my_item, widget)
        self.my_widgets_List_dict[widget.filename] = my_item
        widget.delete.connect(self.delete_widget)
        widget.open.connect(self.readMethod)
        widget.home.connect(self.homepage)
        widget.fav.connect(self.pagefav)
        widget.want_to.connect(self.want)

    # удаляем виджет по нажатию на кнопку
    def delete_widget(self):
        widget = self.sender()
        my_item = self.my_widgets_List_dict[widget.filename]
        cur = self.con.cursor()
        title = cur.execute(f"""SELECT razdel from list_of_books WHERE ssilka = '{widget.filename}'""").fetchone()
        page = str(title[0])
        book = self.lists[str(title[0])]
        book.takeItem(book.row(my_item))
        cur.execute(f"""DELETE from list_of_books WHERE ssilka = '{widget.filename}'""")
        self.con.commit()
        del self.my_widgets_List_dict[widget.filename]
        del self.data[page][self.data[page].index(widget.filename)]

    # переносим книгу на домашнюю страницу
    def homepage(self):
        widget = self.sender()
        my_item = self.my_widgets_List_dict[widget.filename]
        cur = self.con.cursor()
        title = cur.execute(f"""SELECT razdel from list_of_books WHERE ssilka = '{widget.filename}'""").fetchone()
        book = self.lists[str(title[0])]
        page = str(title[0])
        del self.data[page][self.data[page].index(widget.filename)]
        self.data['homeList'].append(widget.filename)
        book.takeItem(book.row(my_item))
        cur.execute(f"""UPDATE list_of_books 
                        SET razdel = 'homeList'
                        WHERE ssilka = '{widget.filename}'""")
        self.con.commit()
        widget = Custom_Widget(widget.filename)
        my_item = QListWidgetItem(self.homeList)
        self.homeList.addItem(my_item)
        self.homeList.setItemWidget(my_item, widget)
        self.my_widgets_List_dict[widget.filename] = my_item
        widget.delete.connect(self.delete_widget)
        widget.open.connect(self.readMethod)
        widget.want_to.connect(self.want)
        widget.reade.connect(self.rad)
        widget.fav.connect(self.pagefav)

    # переносим книгу в любимые
    def pagefav(self):
        widget = self.sender()
        my_item = self.my_widgets_List_dict[widget.filename]
        cur = self.con.cursor()
        title = cur.execute(f"""SELECT razdel from list_of_books WHERE ssilka = '{widget.filename}'""").fetchone()
        book = self.lists[str(title[0])]
        page = str(title[0])
        del self.data[page][self.data[page].index(widget.filename)]
        self.data['favList'].append(widget.filename)
        book.takeItem(book.row(my_item))
        cur.execute(f"""UPDATE list_of_books 
                        SET razdel = 'favList'
                        WHERE ssilka = '{widget.filename}'""")
        self.con.commit()
        widget = Custom_Widget(widget.filename)
        my_item = QListWidgetItem(self.favList)
        self.favList.addItem(my_item)
        self.favList.setItemWidget(my_item, widget)
        self.my_widgets_List_dict[widget.filename] = my_item
        widget.delete.connect(self.delete_widget)
        widget.open.connect(self.readMethod)
        widget.want_to.connect(self.want)
        widget.reade.connect(self.rad)
        widget.home.connect(self.homepage)

    # переносим книгу во вкладку хочу прочитать
    def want(self):
        widget = self.sender()
        my_item = self.my_widgets_List_dict[widget.filename]
        cur = self.con.cursor()
        title = cur.execute(f"""SELECT razdel from list_of_books WHERE ssilka = '{widget.filename}'""").fetchone()
        book = self.lists[str(title[0])]
        page = str(title[0])
        del self.data[page][self.data[page].index(widget.filename)]
        self.data['want_to_readList'].append(widget.filename)
        book.takeItem(book.row(my_item))
        cur.execute(f"""UPDATE list_of_books 
                        SET razdel = 'want_to_readList'
                        WHERE ssilka = '{widget.filename}'""")
        self.con.commit()
        widget = Custom_Widget(widget.filename)
        my_item = QListWidgetItem(self.want_to_readList)
        self.want_to_readList.addItem(my_item)
        self.want_to_readList.setItemWidget(my_item, widget)
        self.my_widgets_List_dict[widget.filename] = my_item
        widget.delete.connect(self.delete_widget)
        widget.open.connect(self.readMethod)
        widget.fav.connect(self.pagefav)
        widget.reade.connect(self.rad)
        widget.home.connect(self.homepage)

    # переносим книгу в прочитанные
    def rad(self):
        widget = self.sender()
        my_item = self.my_widgets_List_dict[widget.filename]
        cur = self.con.cursor()
        title = cur.execute(f"""SELECT razdel from list_of_books WHERE ssilka = '{widget.filename}'""").fetchone()
        book = self.lists[str(title[0])]
        page = str(title[0])
        del self.data[page][self.data[page].index(widget.filename)]
        self.data['readList'].append(widget.filename)
        book.takeItem(book.row(my_item))
        cur.execute(f"""UPDATE list_of_books 
                        SET razdel = 'readList'
                        WHERE ssilka = '{widget.filename}'""")
        self.con.commit()
        widget = Custom_Widget(widget.filename)
        my_item = QListWidgetItem(self.readList)
        self.readList.addItem(my_item)
        self.readList.setItemWidget(my_item, widget)
        self.my_widgets_List_dict[widget.filename] = my_item
        widget.delete.connect(self.delete_widget)
        widget.open.connect(self.readMethod)
        widget.fav.connect(self.pagefav)
        widget.want_to.connect(self.want)
        widget.home.connect(self.homepage)


# создаем класс для окна с чтением
class Reader(QWidget):
    def __init__(self):
        super(Reader, self).__init__()
        uic.loadUi("WindowForRead.ui", self)
        # отслеживаем изменение шрифта
        self.font.activated.connect(self.Font)
        # отслеживаем изменение размера
        self.size.valueChanged.connect(self.Size)
        # по нажатию текст выравнивается по правой стороне
        self.align_right.clicked.connect(lambda: self.textBrowser.setAlignment(Qt.AlignRight))
        # по нажатию текст выравнивается по левой стороне
        self.align_left.clicked.connect(lambda: self.textBrowser.setAlignment(Qt.AlignLeft))
        # по нажатию текст выравнивается по центру
        self.align_center.clicked.connect(lambda: self.textBrowser.setAlignment(Qt.AlignCenter))

    def Font(self):
        font = self.font.currentText()
        self.textBrowser.setCurrentFont(QFont(font))
        value = self.size.value()
        self.textBrowser.setFontPointSize(value)

    def Size(self):
        value = self.size.value()
        self.textBrowser.setFontPointSize(value)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
