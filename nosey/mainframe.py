import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, uic

import nosey
from nosey.monitor import Monitor
from nosey.sources import Sources
from nosey.plot import Plot
from nosey.groups import Groups


class MainFrame(QtGui.QMainWindow, Monitor, Sources, Plot, Groups):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        dirname = os.path.dirname(__file__)
        uic.loadUi(os.path.join(dirname, 'ui/main.ui'), self)


        self.setupUi()
        self.actionUpdate_automatically.trigger()



    # ====================== SLOTS ====================== #

    @QtCore.pyqtSlot()
    def on_actionExit_triggered(self, *args, **kwargs):
        self.close()


    @QtCore.pyqtSlot()
    def on_btn_addRoi_pressed(self, *args, **kwargs):
        self.addRoi()


    @QtCore.pyqtSlot()
    def on_btn_addEnergyPoint_pressed(self, *args, **kwargs):
        self.addEnergyPoint()


    @QtCore.pyqtSlot()
    def on_btn_addSource_pressed(self, *args, **kwargs):
        self.addSource()


    @QtCore.pyqtSlot()
    def on_actionUpdatePlot_triggered(self, *args, **kwargs):
        self.updatePlot(manual = True)


    @QtCore.pyqtSlot()
    def on_actionNormalize_triggered(self, *args, **kwargs):
        self.updatePlot(manual = True)


    @QtCore.pyqtSlot()
    def on_actionSubtractBackground_triggered(self, *args, **kwargs):
        self.updatePlot(manual = True)


    @QtCore.pyqtSlot()
    def on_actionSingleAnalyzers_triggered(self, *args, **kwargs):
        self.updatePlot(manual = True)


    @QtCore.pyqtSlot()
    def on_actionSingleScans_triggered(self, *args, **kwargs):
        self.updatePlot(manual = True)


    @QtCore.pyqtSlot()
    def on_actionScanningType_triggered(self, *args, **kwargs):
        self.updatePlot(manual = True)


    @QtCore.pyqtSlot()
    def on_btn_autoCalibration_clicked(self, *args, **kwargs):
        images = np.empty(1)
        self.autoCalibration()




    def applySettings(self, *args, **kwargs):

        ###################### Plotting ######################
        plotItem = self.plotWidget.getPlotItem()

        # Plot title and labels
        plotTitleSize   = '{}pt'.format(self.spinBox_plotTitleSize.value())
        plotXLabelSize  = '{}pt'.format(self.spinBox_plotXLabelSize.value())
        plotYLabelSize  = '{}pt'.format(self.spinBox_plotYLabelSize.value())

        plotTitle = self.lineEdit_plotTitle.text()
        plotXLabel = self.lineEdit_xLabel.text()
        plotYLabel = self.lineEdit_yLabel.text()
        plotXLabelUnits = self.lineEdit_xLabelUnits.text()
        plotYLabelUnits = self.lineEdit_yLabelUnits.text()

        s = {'color': '#000'}
        plotItem.setTitle(plotTitle, size = plotTitleSize, **s)
        plotItem.getAxis('bottom').setLabel(plotXLabel,
            **{'font-size':plotXLabelSize}, units = plotXLabelUnits, **s)
        plotItem.getAxis('left').setLabel(plotYLabel,
            **{'font-size':plotYLabelSize}, units = plotYLabelUnits, **s)

        plotLineWidth = int(self.spinBox_plotLineWidth.value())

        for item in plotItem.listDataItems():
            pen = item.opts['pen']
            pen.setWidth(plotLineWidth)
            item.setPen(pen)

    # =================================================== #


    def setupUi(self):
        self.setupMonitor()
        self.setupSources()
        self.setupPlot()
        self.setupGroupsFrame()
        self.splitter_2.setStretchFactor(0, 3)

        for recipe in nosey.recipes:
            self.comboBox_analysis_recipes.addItem(recipe.__doc__, recipe)

        # Events
        self.proxies = []
        self.proxies.append(pg.SignalProxy(self.imageView.getView().scene().sigMouseMoved,
            rateLimit=20, slot = self.updateCursorMonitor))

        self.proxies.append(pg.SignalProxy(self.plotWidget.getPlotItem().scene().sigMouseMoved,
            rateLimit=20, slot = lambda e : self.updateCursorPlot(self.plotWidget, e)))
        self.proxies.append(pg.SignalProxy(self.plotWidgetDiff.getPlotItem().scene().sigMouseMoved,
            rateLimit=20, slot = lambda e : self.updateCursorPlot(self.plotWidgetDiff, e)))
        self.proxies.append(pg.SignalProxy(self.plotWidgetIAD.getPlotItem().scene().sigMouseMoved,
            rateLimit=20, slot = lambda e : self.updateCursorPlot(self.plotWidgetIAD, e)))



class EditDialog(QtGui.QDialog):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        dirname = os.path.dirname(__file__)
        uic.loadUi(os.path.join(dirname, 'ui/edit.ui'), self)
