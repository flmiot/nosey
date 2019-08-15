import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, uic

import nosey
import nosey.gui
from nosey.gui.monitor import Monitor
from nosey.gui.sources import Sources
from nosey.gui.plot import Plot
from nosey.gui.groups import Groups
from nosey.gui.settings import Settings
from nosey.gui.references import References


class MainFrame(QtGui.QMainWindow, Monitor, Sources, Plot, Groups, Settings, References):
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
    def on_actionCOMShift_triggered(self, *args, **kwargs):
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



    def setupUi(self):
        self.setupMonitor()
        self.setupSources()
        self.setupPlot()
        self.setupGroupsFrame()
        self.setupSettingTree()
        self.setupReferences()

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
