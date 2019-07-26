import os
from pyqtgraph.Qt import QtGui, QtCore, uic

class Settings(QtGui.QMainWindow):
    def __init__(self, gui, *args, **kwargs):
        super().__init__(*args, **kwargs)
        dirname = os.path.dirname(__file__)
        uic.loadUi(os.path.join(dirname, 'ui/settings.ui'), self)
        self.gui = gui


    @QtCore.pyqtSlot()
    def on_btn_ok_clicked(self, *args, **kwargs):
        self.apply()
        self.close()


    @QtCore.pyqtSlot()
    def on_btn_apply_clicked(self, *args, **kwargs):
        self.apply()


    @QtCore.pyqtSlot()
    def on_btn_cancel_clicked(self, *args, **kwargs):
        self.close()


    def apply(self):

        ###################### Plotting ######################
        plotItem = self.gui.plotWidget.getPlotItem()

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
        plotItem.setTitle(plotTitle, size = plotTitleSize, bold = True, **s)
        plotItem.getAxis('bottom').setLabel(plotXLabel,
            **{'font-size':plotXLabelSize}, units = plotXLabelUnits, **s)
        plotItem.getAxis('left').setLabel(plotYLabel,
            **{'font-size':plotYLabelSize}, units = plotYLabelUnits, **s)

        plotLineWidth = float(self.doubleSpinBox_plotLineWidth.value())

        for item in plotItem.listDataItems():
            pen = item.opts['pen']
            pen.setWidth(plotLineWidth)
            item.setPen(pen)


    def show(self):
        super().show()
