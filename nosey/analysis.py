import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, uic

class AnalysisSetup(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        dirname = os.path.dirname(__file__)
        uic.loadUi(os.path.join(dirname, 'ui/analysis.ui'), self)


    @QtCore.pyqtSlot()
    def on_btn_addSource_pressed(self, *args, **kwargs):
        self.addSource()


    def addSource(self):
        rows = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rows)

        # Button items
        btn_active = QtGui.QPushButton("Active")
        btn_active.setCheckable(True)
        btn_active.toggle()
        btn_active.setStyleSheet("QPushButton:checked { background-color: #a8fc97 }")
        btn_remove = QtGui.QPushButton("Remove")
        btn_remove.setStyleSheet("QPushButton { background-color: #ff7a69 }")
        btn_view = QtGui.QPushButton("View")
        self.tableWidget.setCellWidget(rows, 0, btn_active)
        self.tableWidget.setCellWidget(rows, 1, btn_remove)
        self.tableWidget.setCellWidget(rows, 2, btn_view)

        # Remaining items
        item01 = QtGui.QTableWidgetItem()
        item01.setText("")
        item02 = QtGui.QTableWidgetItem()
        item02.setText("")

        self.tableWidget.setItem(rows, 3, item01)
        self.tableWidget.setItem(rows, 4, item02)

        # Connect button events
