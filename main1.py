import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QTextEdit, QLabel, QWidget, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QSize, QUrl
from PyQt5.QtGui import QFont, QPixmap, QRegExpValidator, QColor
from PyQt5.QtCore import (QCoreApplication, QObject, QRunnable, QThread, QThreadPool, pyqtSignal, pyqtSlot, QTimer, QRegExp)
from PyQt5 import QtCore, QtWidgets
import re
import time
from pygtail import Pygtail
import os
import re

ip_address_regex = re.compile(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(841, 578)
        MainWindow.setMinimumSize(QtCore.QSize(841, 578))
        MainWindow.setMaximumSize(QtCore.QSize(841, 578))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setMinimumSize(QtCore.QSize(550, 0))
        self.tableWidget.setMaximumSize(QtCore.QSize(550, 16777215))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(['IP-адрес', 'Метод', 'Статус', 'Время'])
        self.horizontalLayout.addWidget(self.tableWidget)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit.setObjectName("lineEdit")
        ip_address_validator = QRegExpValidator(QRegExp(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'))
        self.lineEdit.setValidator(ip_address_validator)
        self.lineEdit.setPlaceholderText('127.0.0.1')
        self.verticalLayout_2.addWidget(self.lineEdit)
        self.pushButton_3 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.clicked.connect(self.find)
        self.verticalLayout_2.addWidget(self.pushButton_3)
        self.widget = QtWidgets.QWidget(self.groupBox_2)
        self.widget.setObjectName("widget")
        self.verticalLayout_2.addWidget(self.widget)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QtCore.QSize(0, 50))
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pushButton = QtWidgets.QPushButton(self.groupBox)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_3.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_3.addWidget(self.pushButton_2)
        self.verticalLayout.addWidget(self.groupBox)
        self.horizontalLayout.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Мониторинг сервера Apache"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Поиск записи:"))
        self.pushButton_3.setText(_translate("MainWindow", "Найти"))
        self.groupBox.setTitle(_translate("MainWindow", "Работа с сервером:"))
        self.pushButton.setText(_translate("MainWindow", "Запуск"))
        self.pushButton_2.setText(_translate("MainWindow", "Стоп"))
    
    def find(self):
        str = self.lineEdit.text()
        if str != '':
            for row in range(self.tableWidget.rowCount()):
                item = self.tableWidget.item(row, 0)
                if item and item.text() == str:
                    for col in range(self.tableWidget.columnCount()):
                        self.tableWidget.item(row, col).setBackground(QColor('red'))
        else:
            QMessageBox.critical(self, 'Ошибка', 'Введите IP-адрес для поиска')
    
class Find(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.run)
        self.ui.pushButton_2.clicked.connect(self.stop)
        self.thread = QtCore.QThread()
        self.thread.start()
        self.setCentralWidget(self.ui.centralwidget)
        self.running = True
        self.start_time = time.time()  

    @QtCore.pyqtSlot()
    def run(self):
        self.running = True
        log_path = "C:/xampp/apache/logs/access.log"
        if os.path.exists(log_path):
            apache_log_pattern = r'^(\S+) (\S+) (\S+) \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+)\s*(\S*)" (\d{3}) (\d+|-)\s*"([^"]*)" "([^"]*)"'
            apache_log_regex = re.compile(apache_log_pattern)
            self.timer = QTimer(self)  
            self.timer.timeout.connect(self.check_new_records)  
            self.timer.start(1000)  
            for line in Pygtail(log_path):
                if not self.running:
                    return
                match = apache_log_regex.match(line)
                if match:
                    timestamp = time.mktime(time.strptime(match.group(4), "%d/%b/%Y:%H:%M:%S %z"))
                    if timestamp < self.start_time:
                        continue  
                    ip_address = match.group(1)
                    method = match.group(5)
                    status_code = match.group(8)
                    current_row = self.ui.tableWidget.rowCount()
                    self.ui.tableWidget.insertRow(current_row)
                    self.ui.tableWidget.setItem(current_row, 0, QtWidgets.QTableWidgetItem(ip_address))
                    self.ui.tableWidget.setItem(current_row, 1, QtWidgets.QTableWidgetItem(method))
                    self.ui.tableWidget.setItem(current_row, 2, QtWidgets.QTableWidgetItem(status_code))
                    self.ui.tableWidget.setItem(current_row, 3, QtWidgets.QTableWidgetItem(time.strftime("%H:%M:%S", time.localtime(timestamp))))
                    QtWidgets.QApplication.processEvents()
        else:
            QMessageBox.critical(self, 'Ошибка', 'Файл логов Apache не найден')
            return

    @QtCore.pyqtSlot()
    def check_new_records(self):
        log_path = "C:/xampp/apache/logs/access.log"
        if os.path.exists(log_path):
            apache_log_pattern = r'^(\S+) (\S+) (\S+) \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+)\s*(\S*)" (\d{3}) (\d+|-)\s*"([^"]*)" "([^"]*)"'
            apache_log_regex = re.compile(apache_log_pattern)
            for line in Pygtail(log_path):
                if not self.running:
                    return
                match = apache_log_regex.match(line)
                if match:
                    timestamp = time.mktime(time.strptime(match.group(4), "%d/%b/%Y:%H:%M:%S %z"))
                    if timestamp < self.start_time:
                        continue  
                    ip_address = match.group(1)
                    method = match.group(5)
                    status_code = match.group(8)
                    current_row = self.ui.tableWidget.rowCount()
                    self.ui.tableWidget.insertRow(current_row)
                    self.ui.tableWidget.setItem(current_row, 0, QtWidgets.QTableWidgetItem(ip_address))
                    self.ui.tableWidget.setItem(current_row, 1, QtWidgets.QTableWidgetItem(method))
                    self.ui.tableWidget.setItem(current_row, 2, QtWidgets.QTableWidgetItem(status_code))
                    self.ui.tableWidget.setItem(current_row, 3, QtWidgets.QTableWidgetItem(time.strftime("%H:%M:%S", time.localtime(timestamp))))
                    QtWidgets.QApplication.processEvents()
        else:
            QMessageBox.critical(self, 'Ошибка', 'Файл логов Apache не найден')
            return

    @QtCore.pyqtSlot()
    def stop(self):
        self.running = False
        self.timer.stop()  # Останавливаем таймер при нажатии кнопки "Стоп"


    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Find()
    w.show()
    sys.exit(app.exec_()) 