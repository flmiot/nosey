import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from nosey.gui.templates import HideButton, RemoveButton, ExtRef1Button, ExtRef2Button

import nosey

class References(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def setupReferences(self):
        pass


    def addExternalReference(self):
        paths = QtGui.QFileDialog.getOpenFileNames(self, 'Select files')[0]

        for path in paths:
            rows = self.tableExternalReferences.rowCount()
            self.tableExternalReferences.insertRow(rows)
            filename = os.path.split(path)[1]

            data = np.loadtxt(path, skiprows = 1).T

            # Button items
            btn_active      = HideButton()
            btn_active.toggle()
            btn_remove      = RemoveButton()
            btn_setAsRef1   = ExtRef1Button()
            btn_setAsRef2   = ExtRef2Button()

            self.tableExternalReferences.setCellWidget(rows, 0, btn_active)
            self.tableExternalReferences.setCellWidget(rows, 1, btn_remove)
            self.tableExternalReferences.setCellWidget(rows, 2, btn_setAsRef1)
            self.tableExternalReferences.setCellWidget(rows, 3, btn_setAsRef2)
            item = QtGui.QTableWidgetItem()
            item.setText(filename)
            item.setData(pg.QtCore.Qt.UserRole, data)
            self.tableExternalReferences.setItem(rows, 4, item)
            self.tableExternalReferences.resizeColumnsToContents()

            # Events
            btn_active.clicked.connect(self.updatePlot)
            btn_remove.clicked.connect(lambda : self.removeExternalReference(item))
            btn_setAsRef1.clicked.connect(lambda : self.setAsRef(item, 1))
            btn_setAsRef2.clicked.connect(lambda : self.setAsRef(item, 2))



    def setAsRef(self, item, refID):
        try:
            if refID in [1,2]:
                col = refID + 1
                otherID = (set([1,2]) - set([refID])).pop()
            else:
                raise ValueError("Invalid external reference requested.")

            try:
                clicked_row = self.tableExternalReferences.row(item)
                if self.getExternalReferenceGroupIndex(otherID) == clicked_row:
                    self.tableExternalReferences.cellWidget(clicked_row, col).setChecked(False)
                    fmt = "External reference can only be either reference 1 or 2."
                    raise RuntimeError(fmt)

            except IndexError as e:
                for row in range(self.tableExternalReferences.rowCount()):
                    if item == self.tableExternalReferences.item(row, 4):
                        continue
                    else:
                        self.tableExternalReferences.cellWidget(row, col).setChecked(False)

            self.updatePlot()
        except RuntimeError as e:
            nosey.Log.error(e)




    def getExternalReferenceGroupIndex(self, refID):
        if refID in [1,2]:
            col = refID + 1
        else:
            raise Exception("Invalid external reference requested.")

        for row in range(self.tableExternalReferences.rowCount()):
            if self.tableExternalReferences.cellWidget(row, col).isChecked():
                return row

        raise IndexError("External reference {} not set!".format(refID))


    def removeExternalReference(self, item):
        row = self.tableExternalReferences.row(item)
        self.tableExternalReferences.removeRow(row)
        self.updatePlot()


    def getExternalReferenceData(self):
        data = []
        for row in range(self.tableExternalReferences.rowCount()):
            if self.tableExternalReferences.cellWidget(row, 0).isChecked():
                item = self.tableExternalReferences.item(row, 4)
                x, y = item.data(pg.QtCore.Qt.UserRole)
                label = item.text()
                data.append([x, y, label])

        return data


    def getSelectedExternalReferenceData(self, refID):
        rowIndex = self.getExternalReferenceGroupIndex(refID)
        item = self.tableExternalReferences.item(rowIndex, 4)
        return item.data(pg.QtCore.Qt.UserRole)



    # def updateSettingsComboBoxes(self):
    #     for c in ['A', 'B']:
    #         item        = self.findItem(['Fraction fitting', 'Components', c])
    #         comboBox   = self.treeWidget.itemWidget(item, 1)
    #         currentlySelectedIndex = comboBox.currentIndex()
    #         currentlySelectedItem = comboBox.itemData(currentlySelectedIndex)
    #         comboBox.clear()
    #         for row in range(self.tableExternalReferences.rowCount()):
    #             item = self.tableExternalReferences.item(row, 4)
    #             comboBox.addItem(item.text(), item)
    #             if item == currentlySelectedItem:
    #                 comboBox.setCurrentIndex(row)
