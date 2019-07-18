import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, uic

from nosey.rois import ROI

class Monitor(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        dirname = os.path.dirname(__file__)
        uic.loadUi(os.path.join(dirname, 'ui/monitor.ui'), self)

        # Placeholder image
        img = np.zeros((512,512))
        self.imageView.setImage(img)


    @QtCore.pyqtSlot()
    def on_actionAdd_ROI_triggered(self, *args, **kwargs):
        self.addRoi()


    def addRoi(self):
        rows = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rows)

        r = ROI([250,250], [250,40], 'ROI {}'.format(rows))
        r.addToMonitor(self)

        # Button items
        btn_active = QtGui.QPushButton("Active")
        btn_active.setCheckable(True)
        btn_active.toggle()
        btn_active.setStyleSheet("QPushButton:checked { background-color: #a8fc97 }")
        btn_remove = QtGui.QPushButton("Remove")
        btn_remove.setStyleSheet("QPushButton { background-color: #ff7a69 }")
        self.tableWidget.setCellWidget(rows, 0, btn_active)
        self.tableWidget.setCellWidget(rows, 1, btn_remove)

        # Remaining items
        item01 = QtGui.QTableWidgetItem()
        item01.setText(r.name)
        item01.setData(pg.QtCore.Qt.UserRole, r)
        item01.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.tableWidget.setItem(rows, 2, item01)

        # Connect button events
        btn_remove.clicked.connect(lambda : self.removeROI(item01))
        btn_active.toggled.connect(r.toggle)


    def removeROI(self, item):
        row = self.tableWidget.row(item)
        roi = item.data(pg.QtCore.Qt.UserRole)
        roi.removeFromMonitor(self)
        self.tableWidget.removeRow(row)


        # Rename remaining ROI
        for row in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(row, 2)
            item.setFlags(QtCore.Qt.ItemIsEditable)
            roi = item.data(pg.QtCore.Qt.UserRole)
            roi.name = 'ROI {}'.format(row)
            item.setText(roi.name)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
