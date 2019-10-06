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

    def setupGroupsFrame(self):
        self.tableGroups.cellChanged.connect(self.updateSourceComboBoxes)

    def addGroup(self, e=None, name=None, active=True, reference=False):

        if name is None:
            name = "Unnamed group"

        rows = self.tableGroups.rowCount()
        self.tableGroups.insertRow(rows)

        # Button items
        btn_active = HideButton()
        btn_active.toggle()
        btn_remove = RemoveButton()
        btn_reference = RefButton()

        self.tableGroups.setCellWidget(rows, 0, btn_active)
        self.tableGroups.setCellWidget(rows, 1, btn_remove)
        self.tableGroups.setCellWidget(rows, 2, btn_reference)
        item01 = QtGui.QTableWidgetItem()
        item01.setText(name)
        self.tableGroups.setItem(rows, 3, item01)
        self.tableGroups.resizeColumnsToContents()
        self.updateSourceComboBoxes()

        # Events
        btn_active.clicked.connect(lambda: self.toggleGroup(item01))
        btn_remove.clicked.connect(lambda: self.removeGroup(item01))
        btn_reference.clicked.connect(lambda: self.setRefGroup(item01))

        if active is False:
            btn_active.toggle()

        if reference is True:
            btn_reference.toggle()
            self.setRefGroup(item01, update=False)

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

    def toggleGroup(self, item, update=True):
        if update:
            self.updatePlot()

    def removeGroup(self, item):
        if self.tableGroups.rowCount() > 1:
            row = self.tableGroups.row(item)
            self.tableGroups.removeRow(row)
            self.updateSourceComboBoxes()
            self.updatePlot()

    def setRefGroup(self, item, update=True):
        if self.getReferenceGroupIndex() is None:
            row = self.tableGroups.row(item)
            self.tableGroups.cellWidget(row, 2).setChecked(True)
        else:
            for grow in range(self.tableGroups.rowCount()):
                if item == self.tableGroups.item(grow, 3):
                    continue
                else:
                    self.tableGroups.cellWidget(grow, 2).setChecked(False)
        if update:
            self.updatePlot()

    def getReferenceGroupIndex(self):
        for grow in range(self.tableGroups.rowCount()):
            if self.tableGroups.cellWidget(grow, 2).isChecked():
                return grow
        return None

    def getSaveString(self):
        saveString = "! GROUPS\n"
        for grow in range(self.tableGroups.rowCount()):
            name = '"{}"'.format(self.tableGroups.item(grow, 3).text())
            p = {
                "include": self.tableGroups.cellWidget(grow, 0).isChecked(),
                "reference": grow == self.getReferenceGroupIndex(),
                "name": name
            }

            subString = "group(\n"
            subString += "\t{}={},\n" * (len(p.keys()) - 1)
            subString += "\t{}={}\n)\n"
            mixed = [
                v for sublist in zip(
                    p.keys(),
                    p.values()) for v in sublist]
            subString = subString.format(*mixed)
            saveString += subString

        saveString += "\n"
        return saveString
