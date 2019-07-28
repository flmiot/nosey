import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, uic

from nosey.roi import ROI
import nosey.guard
from nosey.templates import HideButton, RemoveButton, RefButton

class Groups(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.groups = [True]

    def setupGroupsFrame(self):
        self.tableGroups.cellChanged.connect(self.updateSourceComboBoxes)
        self.addPlottingGroup()
        self.tableGroups.cellWidget(0, 2).toggle()

    def addPlottingGroup(self):
        rows = self.tableGroups.rowCount()
        self.tableGroups.insertRow(rows)

        plottingGroupName = "Unnamed group"
        self.groups.append(True)

        # Button items
        btn_active      = HideButton()
        btn_active.toggle()
        btn_remove      = RemoveButton()
        btn_reference   = RefButton()

        self.tableGroups.setCellWidget(rows, 0, btn_active)
        self.tableGroups.setCellWidget(rows, 1, btn_remove)
        self.tableGroups.setCellWidget(rows, 2, btn_reference)
        item01 = QtGui.QTableWidgetItem()
        item01.setText(plottingGroupName)
        self.tableGroups.setItem(rows, 3, item01)
        self.tableGroups.resizeColumnsToContents()
        self.updateSourceComboBoxes()

        # Events
        btn_active.clicked.connect(lambda : self.toggleGroup(item01))
        btn_remove.clicked.connect(lambda : self.removeGroup(item01))
        btn_reference.clicked.connect(lambda : self.setRefGroup(item01))



    def updateSourceComboBoxes(self):
        for srow in range(self.tableSources.rowCount()):
            comboBox = self.tableSources.cellWidget(srow, 2)
            currentlySelectedIndex = comboBox.currentIndex()
            currentlySelectedItem = comboBox.itemData(currentlySelectedIndex)
            comboBox.clear()
            for grow in range(self.tableGroups.rowCount()):
                item = self.tableGroups.item(grow, 3)
                comboBox.addItem(item.text(), item)
                if item == currentlySelectedItem:
                    comboBox.setCurrentIndex(grow)


    def toggleGroup(self, item):
        row = self.tableGroups.row(item)
        self.groups[row] = self.tableGroups.cellWidget(row, 0).isChecked()
        self.updatePlot()


    def removeGroup(self, item):
        if self.tableGroups.rowCount() > 1:
            row = self.tableGroups.row(item)
            del self.groups[row]
            self.tableGroups.removeRow(row)
            self.updateSourceComboBoxes()
            self.updatePlot()

    def setRefGroup(self, item):
        if self.getReferenceGroupIndex() is None:
            row = self.tableGroups.row(item)
            self.tableGroups.cellWidget(row, 2).setChecked(True)
        else:
            for grow in range(self.tableGroups.rowCount()):
                if item == self.tableGroups.item(grow, 3):
                    continue
                else:
                    self.tableGroups.cellWidget(grow, 2).setChecked(False)


    def getReferenceGroupIndex(self):
        for grow in range(self.tableGroups.rowCount()):
            if self.tableGroups.cellWidget(grow, 2).isChecked():
                return grow
        return None
