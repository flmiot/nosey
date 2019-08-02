import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

import nosey

class Settings(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def setupSettingTree(self):
            self.treeWidget.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)

            # Add widgets: QComboBoxes
            item = self.findItem(['Data import', 'Module'])
            comboBox = QtGui.QComboBox()
            self.treeWidget.setItemWidget(item, 1, comboBox)
            for recipe in nosey.recipes:
                comboBox.addItem(recipe.__doc__, recipe)


            # QSpinBox
            flags = QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive
            items = []
            items = self.treeWidget.findItems('size', flags)
            for item in items:
                spinBox = QtGui.QSpinBox()
                spinBox.setValue(16)
                spinBox.valueChanged.connect(self.applySettings)
                self.treeWidget.setItemWidget(item, 1, spinBox)

            items = self.treeWidget.findItems('thickness', flags)
            for item in items:
                spinBox = QtGui.QSpinBox()
                spinBox.setValue(1)
                spinBox.valueChanged.connect(self.applySettings)
                self.treeWidget.setItemWidget(item, 1, spinBox)

            items = self.treeWidget.findItems('Order', flags)
            for item in items:
                spinBox = QtGui.QSpinBox()
                spinBox.setValue(3)
                spinBox.valueChanged.connect(self.applySettings)
                self.treeWidget.setItemWidget(item, 1, spinBox)

            items = self.treeWidget.findItems('Offset', flags)
            for item in items:
                spinBox = QtGui.QSpinBox()
                spinBox.setValue(20)
                spinBox.valueChanged.connect(self.applySettings)
                self.treeWidget.setItemWidget(item, 1, spinBox)


    def settingsChangedHandler(self, item, column):
        # Remaining events: self.updatePlot
        items = []
        items.append(self.findItem(['Normalization', 'Window', 'Start']))
        items.append(self.findItem(['Normalization', 'Window', 'End']))
        items.append(self.findItem(['Center-of-mass shift', 'Window', 'Start']))
        items.append(self.findItem(['Center-of-mass shift', 'Window', 'End']))
        items.append(self.findItem(['IAD analysis', 'Enabled']))
        items.append(self.findItem(['Difference', 'Enabled']))
        items.append(self.findItem(['Background subtraction', 'Polynomial fitting', 'Enabled']))

        if item in items:
            self.updatePlot()
            return

        items = []
        items.append(self.findItem(['Plot settings', 'Title', 'Text']))
        items.append(self.findItem(['Plot settings', 'Axis labels', 'X axis', 'Text']))
        items.append(self.findItem(['Plot settings', 'Axis labels', 'Y axis', 'Text']))
        items.append(self.findItem(['Plot settings', 'Axis labels', 'X axis', 'Units']))
        items.append(self.findItem(['Plot settings', 'Axis labels', 'Y axis', 'Units']))

        if item in items:
            self.applySettings()
            return



    def applySettings(self, *args, **kwargs):

        ###################### Plotting ######################
        plotItem = self.plotWidget.getPlotItem()

        # Plot title and labels
        plotTitleSize   = '{}pt'.format(self.getSetting(['Plot settings', 'Title', 'Font size']))
        plotXLabelSize  = '{}pt'.format(self.getSetting(['Plot settings', 'Axis labels', 'Font size']))
        plotYLabelSize  = '{}pt'.format(self.getSetting(['Plot settings', 'Axis labels', 'Font size']))

        plotTitle = self.getSetting(['Plot settings', 'Title', 'Text'])
        plotXLabel = self.getSetting(['Plot settings', 'Axis labels', 'X axis', 'Text'])
        plotYLabel = self.getSetting(['Plot settings', 'Axis labels', 'Y axis', 'Text'])
        plotXLabelUnits = self.getSetting(['Plot settings', 'Axis labels', 'X axis', 'Units'])
        plotYLabelUnits = self.getSetting(['Plot settings', 'Axis labels', 'Y axis', 'Units'])

        s = {'color': '#000'}
        plotItem.setTitle(plotTitle, size = plotTitleSize, **s)
        plotItem.getAxis('bottom').setLabel(plotXLabel,
            **{'font-size':plotXLabelSize}, units = plotXLabelUnits, **s)
        plotItem.getAxis('left').setLabel(plotYLabel,
            **{'font-size':plotYLabelSize}, units = plotYLabelUnits, **s)

        plotLineWidth = int(self.getSetting(['Plot settings', 'Line thickness']))

        for item in plotItem.listDataItems():
            pen = item.opts['pen']
            pen.setWidth(plotLineWidth)
            item.setPen(pen)

    # =================================================== #


    def getSetting(self, strings):
        item    = self.findItem(strings)
        widget  = self.treeWidget.itemWidget(item, 1)

        if widget is None:
            if bool(QtCore.Qt.ItemIsUserCheckable & item.flags()):
                return item.checkState(1) == QtCore.Qt.Checked
            else:
                return item.text(1)
        else:
            if isinstance(widget, QtGui.QSpinBox):
                return widget.value()
            elif isinstance(widget, QtGui.QLineEdit):
                return widget.text()
            elif isinstance(widget, QtGui.QComboBox):
                return widget.currentData()
            else:
                raise Exception("Unknown setting type requested.")


    def findItem(self, strings, items = []):
        flags       = QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive
        matches     = self.treeWidget.findItems(strings[0], flags)

        if items != []:
            matches = list([i for i in matches if i.parent() in items])

        if len(matches) == 0 or len(strings) == 0:
            raise Exception('Invalid QTreeWidget item path')
        elif len(matches) == 1 and len(strings) == 1:
            return matches[0]
        else:

            return self.findItem(strings[1::], matches)
