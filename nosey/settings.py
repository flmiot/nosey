import numpy as np
from pyqtgraph.Qt import QtCore, QtGui

import nosey


class Settings(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def getKeywordMap(self):
        keywordMap = {
            "import-module": ['Data import', 'Module'],
            "sum-before-calibration": ['Energy calibration', 'Sum runs before search'],
            "search-radius": ['Energy calibration', 'Search radius'],
            "iad": ['IAD analysis', 'Enabled'],
            "normalization-start": ['Normalization', 'Window', 'Start'],
            "normalization-end": ['Normalization', 'Window', 'End'],
            "fraction-fitting": ['Fraction fitting', 'Enabled'],
            "difference": ['Difference', 'Enabled'],
            "com-start": ['Center-of-mass shift', 'Window', 'Start'],
            "com-end": ['Center-of-mass shift', 'Window', 'End'],
            "fit-bg": ['Background subtraction', 'Polynomial fitting', 'Enabled'],
            "title-fontsize": ['Plot settings', 'Title', 'Font size'],
            "x-label-size": ['Plot settings', 'Axis labels', 'Font size'],
            "y-label-size": ['Plot settings', 'Axis labels', 'Font size'],
            "tick-label-size": ['Plot settings', 'Tick labels', 'Font size'],
            "title": ['Plot settings', 'Title', 'Text'],
            "xlabel": ['Plot settings', 'Axis labels', 'X axis', 'Text'],
            "ylabel": ['Plot settings', 'Axis labels', 'Y axis', 'Text'],
            "xlabel-units": ['Plot settings', 'Axis labels', 'X axis', 'Units'],
            "ylabel-units": ['Plot settings', 'Axis labels', 'Y axis', 'Units'],
            "tick-text-offset": ['Plot settings', 'Tick labels', 'Offset'],
            "line-thickness": ['Plot settings', 'Line thickness']
        }

        return keywordMap

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
            spinBox.valueChanged.connect(self.applySettings)
            self.treeWidget.setItemWidget(item, 1, spinBox)

        # Set font sizes
        self.setSetting(['Plot settings', 'Title', 'Font size'], 16)
        self.setSetting(['Plot settings', 'Axis labels', 'Font size'], 14)
        self.setSetting(['Plot settings', 'Tick labels', 'Font size'], 12)

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
            spinBox.valueChanged.connect(self.updatePlot)
            self.treeWidget.setItemWidget(item, 1, spinBox)

        items = self.treeWidget.findItems('Offset', flags)
        for item in items:
            spinBox = QtGui.QSpinBox()
            spinBox.setValue(35)
            spinBox.valueChanged.connect(self.applySettings)
            self.treeWidget.setItemWidget(item, 1, spinBox)

    def settingsChangedHandler(self, item, column):
        # Remaining events: self.updatePlot
        items = []
        items.append(self.findItem(['Normalization', 'Window', 'Start']))
        items.append(self.findItem(['Normalization', 'Window', 'End']))
        items.append(self.findItem(
            ['Center-of-mass shift', 'Window', 'Start']))
        items.append(self.findItem(['Center-of-mass shift', 'Window', 'End']))
        items.append(self.findItem(['IAD analysis', 'Enabled']))
        items.append(self.findItem(['Difference', 'Enabled']))
        items.append(self.findItem(
            ['Background subtraction', 'Polynomial fitting', 'Enabled']))
        items.append(self.findItem(['Fraction fitting', 'Enabled']))

        if item in items:
            self.updatePlot()
            return

        items = []
        items.append(self.findItem(['Plot settings', 'Title', 'Text']))
        items.append(self.findItem(
            ['Plot settings', 'Axis labels', 'X axis', 'Text']))
        items.append(self.findItem(
            ['Plot settings', 'Axis labels', 'Y axis', 'Text']))
        items.append(self.findItem(
            ['Plot settings', 'Axis labels', 'X axis', 'Units']))
        items.append(self.findItem(
            ['Plot settings', 'Axis labels', 'Y axis', 'Units']))

        if item in items:
            self.applySettings()
            return

    def applySettings(self, *args, **kwargs):

        plotItem = self.plotWidget.getPlotItem()

        # Plot title and labels
        plotTitleSize = '{}pt'.format(self.getSetting(
            ['Plot settings', 'Title', 'Font size']))
        plotXLabelSize = '{}pt'.format(self.getSetting(
            ['Plot settings', 'Axis labels', 'Font size']))
        plotYLabelSize = '{}pt'.format(self.getSetting(
            ['Plot settings', 'Axis labels', 'Font size']))
        tickLabelSize = self.getSetting(
            ['Plot settings', 'Tick labels', 'Font size'])

        plotTitle = self.getSetting(['Plot settings', 'Title', 'Text'])
        plotXLabel = self.getSetting(
            ['Plot settings', 'Axis labels', 'X axis', 'Text'])
        plotYLabel = self.getSetting(
            ['Plot settings', 'Axis labels', 'Y axis', 'Text'])
        plotXLabelUnits = self.getSetting(
            ['Plot settings', 'Axis labels', 'X axis', 'Units'])
        plotYLabelUnits = self.getSetting(
            ['Plot settings', 'Axis labels', 'Y axis', 'Units'])
        tickTextOffset = self.getSetting(
            ['Plot settings', 'Tick labels', 'Offset'])

        s = {'color': '#000'}
        plotItem.setTitle(plotTitle, size=plotTitleSize, **s)
        plotItem.getAxis('bottom').setLabel(
            plotXLabel, **{'font-size': plotXLabelSize}, units=plotXLabelUnits, **s)
        plotItem.getAxis('left').setLabel(
            plotYLabel, **{'font-size': plotYLabelSize}, units=plotYLabelUnits, **s)

        plotItem.getAxis('left').setTickFont(
            QtGui.QFont('Tahoma', tickLabelSize))
        plotItem.getAxis('left').setStyle(
            autoExpandTextSpace=False,
            tickTextWidth=tickTextOffset)
        plotItem.getAxis('bottom').setTickFont(
            QtGui.QFont('Tahoma', tickLabelSize))
        plotItem.getAxis('bottom').setStyle(
            autoExpandTextSpace=False, tickTextHeight=int(
                tickTextOffset * 18 / 30))

        plotLineWidth = int(self.getSetting(
            ['Plot settings', 'Line thickness']))

        for item in plotItem.listDataItems():
            pen = item.opts['pen']
            pen.setWidth(plotLineWidth)
            item.setPen(pen)

    def getSetting(self, strings):
        item = self.findItem(strings)
        widget = self.treeWidget.itemWidget(item, 1)

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

    def setSetting(self, strings, value):
        item = self.findItem(strings)
        widget = self.treeWidget.itemWidget(item, 1)

        if widget is None:
            if bool(QtCore.Qt.ItemIsUserCheckable & item.flags()):
                item.setCheckState(1, bool(value))
            else:
                item.setText(1, value)
        else:
            if isinstance(widget, QtGui.QSpinBox):
                widget.setValue(float(value))
            elif isinstance(widget, QtGui.QLineEdit):
                widget.setText(str(value))
            elif isinstance(widget, QtGui.QComboBox):
                widget.setCurrentText(str(value))
            else:
                Exception("Unknown setting type requested.")

    def findItem(self, strings, items=[]):
        flags = QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive
        matches = self.treeWidget.findItems(strings[0], flags)

        if items != []:
            matches = list([i for i in matches if i.parent() in items])

        if len(matches) == 0 or len(strings) == 0:
            raise Exception('Invalid QTreeWidget item path')
        elif len(matches) == 1 and len(strings) == 1:
            return matches[0]
        else:

            return self.findItem(strings[1::], matches)

    def getSaveString(self):
        saveString = "! SETTINGS\n"
        p = {}
        for key, value in self.getKeywordMap().items():
            p[key] = self.getSetting(value)

        subString = "settings(\n"
        subString += "\t{}={},\n" * (len(p.keys()) - 1)
        subString += "\t{}={}\n)\n"
        mixed = [v for sublist in zip(p.keys(), p.values()) for v in sublist]
        subString = subString.format(*mixed)
        saveString += subString
        saveString += "\n"
        return saveString
