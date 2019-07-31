import os
import time
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import matplotlib.cm as cm

import nosey.guard
from nosey.analysis.experiment import Experiment
from nosey.analysis.analyzer import Analyzer
import nosey.analysis.math as nmath

import matplotlib.pyplot as plt

class Plot(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plot = None

    def setupPlot(self):
        self.plotWidget.getPlotItem().addLegend()
        self.plotWidget.setBackground('w')
        self.plotWidget.getAxis('left').enableAutoSIPrefix(False)
        self.plotWidget.getAxis('bottom').enableAutoSIPrefix(False)
        self.plotWidget.getAxis('left').setStyle(tickTextWidth = 50)
        self.plotWidget.getAxis('bottom').setStyle(tickTextOffset = 10)
        self.plotWidget.getAxis('bottom')
        self.plotWidget.getAxis('left').setPen(color = 'k')
        self.plotWidget.getAxis('bottom').setPen(color = 'k')

        self.plotWidgetDiff.getPlotItem().addLegend()
        self.plotWidgetDiff.setBackground('w')
        self.plotWidgetDiff.getAxis('left').enableAutoSIPrefix(False)
        self.plotWidgetDiff.getAxis('bottom').enableAutoSIPrefix(False)
        self.plotWidgetDiff.getAxis('left').setStyle(tickTextWidth = 50)
        self.plotWidgetDiff.getAxis('bottom').setStyle(tickTextOffset = 10)
        self.plotWidgetDiff.getAxis('bottom')
        self.plotWidgetDiff.getAxis('left').setPen(color = 'k')
        self.plotWidgetDiff.getAxis('bottom').setPen(color = 'k')

        self.plotWidgetIAD.setBackground('w')
        self.plotWidgetIAD.getAxis('left').enableAutoSIPrefix(False)
        self.plotWidgetIAD.getAxis('bottom').enableAutoSIPrefix(False)
        self.plotWidgetIAD.getAxis('left').setStyle(tickTextWidth = 50)
        self.plotWidgetIAD.getAxis('bottom').setStyle(tickTextOffset = 10)
        self.plotWidgetIAD.getAxis('bottom')
        self.plotWidgetIAD.getAxis('left').setPen(color = 'k')
        self.plotWidgetIAD.getAxis('bottom').setPen(color = 'k')


    @nosey.guard.updateGuard
    def updatePlot(self, *args, **kwargs):
        try:
            start = time.time()
            analyzers   = []
            calcIAD     = self.analysis_checkBox_doIAD.isChecked()
            w0   = float(self.analysis_lineEdit_window0.text())
            w1   = float(self.analysis_lineEdit_window1.text())
            if self.analysis_checkBox_polyFit.isChecked():
                poly_order  = int(self.analysis_spinBox_polyOrder.value())
            else:
                poly_order  = None

            results     = []
            valuesIAD   = []

            refIndex        = self.getReferenceGroupIndex()
            refResult       = None

            groupIndex  = 0
            run         = 0
            groups      = self.tableGroups.rowCount()
            while groupIndex < groups:

                # Calculate and plot reference first
                if refResult is None and groupIndex != refIndex:
                    groupIndex += 1
                    continue

                if refResult is not None and groupIndex == refIndex:
                    groupIndex += 1
                    continue

                # Skip this group if hidden
                if not self.tableGroups.cellWidget(groupIndex, 0).isChecked():
                    if groupIndex == refIndex:
                        raise Exception("Reference group is hidden!")
                    groupIndex += 1
                    continue

                self.statusBar.setProgressBarFraction((run + 1) / groups)

                group               = self.tableGroups.item(groupIndex, 3)
                experiment          = Experiment()
                experiment.scans    = self.getScans(group = group)

                # Skip this group if no scans are assigned
                if len(experiment.scans) < 1:
                    if groupIndex == refIndex:
                        raise Exception("Reference group has no scans!")
                    groupIndex += 1
                    continue

                roi = self.getROI()
                for r in roi:
                    if not r.active:
                        continue

                    sig = Analyzer.make_signal_from_QtRoi(r, [195, 487], self.imageView, 0)
                    energies = self.getEnergies()

                    if len(energies) >= 2:
                        positions = r.getEnergyPointPositions()
                        sig.setEnergies(positions, energies)

                    bg01 = Analyzer.make_signal_from_QtRoi(r, [195, 487], self.imageView, 1)
                    bg02 = Analyzer.make_signal_from_QtRoi(r, [195, 487], self.imageView, 2)

                    experiment.analyzers.append(sig)
                    experiment.bg_roi.append( (bg01, bg02) )

                result = experiment.get_spectrum()

                if calcIAD and groupIndex != refIndex:
                    w0COM = float(self.analysis_lineEdit_COMwindow0.text())
                    w1COM = float(self.analysis_lineEdit_COMwindow1.text())
                    iad = result.getIAD(refResult, windowNorm = [w0, w1], windowCOM = [w0COM, w1COM])
                    valuesIAD.append(iad)

                results.append( result )

                groupName = self.tableGroups.item(groupIndex, 3).text()
                if refResult is None:
                    fmt = "Reference group '{}' calculated".format(groupName)
                    nosey.Log.info(fmt)
                    refResult = result
                    groupIndex = 0
                else:
                    fmt = "Non-reference group '{}' calculated".format(groupName)
                    nosey.Log.info(fmt)
                    groupIndex += 1

                if len(results) == 0:
                    raise Exception("No active plotting group!")

                run += 1


                # Plot data:
                single_scans    = nosey.gui.actionSingleScans.isChecked()
                single_analyzers = nosey.gui.actionSingleAnalyzers.isChecked()
                subtract_background = nosey.gui.actionSubtractBackground.isChecked()
                normalize       = nosey.gui.actionNormalize.isChecked()
                scanning_type   = nosey.gui.actionScanningType.isChecked()
                com_shift       = nosey.gui.actionCOMShift.isChecked()
                slices          = 1
                single_image    = None

                self.clear_plot()


                if calcIAD:
                    self.plotWidgetIAD.plot(range(len(valuesIAD)), valuesIAD,  symbol='o', symbolPen='r')

                self._plot(results, single_analyzers, single_scans,
                    scanning_type, subtract_background, normalize, single_image,
                    slices, False, False, poly_order, com_shift)

                for roi in self.getROI():
                    roi.connectUpdateSlotProxy(self.updatePlot)

            self.statusBar.setProgressBarFraction(1)
            nosey.lastComputationTime = time.time() - start
            fmt = "Last computation took {:.3f} s.".format(nosey.lastComputationTime)
            self.analysis_labelComputation.setText(fmt)

        except Exception as e:
            fmt = 'Plot update failed: {}'.format(e)
            nosey.Log.error(fmt)


    def _plot(self, data, single_analyzers = True, single_scans = True,
        scanning_type = False, subtract_background = True, normalize = False,
        single_image = None, slices = 1, normalize_scans = False,
        normalize_analyzers = False, poly_order = None, com_shift = False):

        groups = len(data)
        w0   = float(self.analysis_lineEdit_window0.text())
        w1   = float(self.analysis_lineEdit_window1.text())

        for ind, d in enumerate(data):

            e, i, b, l = d.get_curves(
                single_scans, single_analyzers,
                scanning_type, single_image, slices,
                normalize_scans, normalize_analyzers, poly_order)

            if ind == 0:
                ref_e, ref_i, ref_b = e, i, b

            pens, pens_bg = self._get_pens(e, i, b, single_analyzers, single_scans, groups)

            if groups > 1:
                pens    = pens[ind]
                pens_bg = pens_bg[ind]

            z1 = zip(range(len(e)), e, i, b, l)
            for ind_s, energy, intensity, background, label in z1:
                # Plot analyzers
                z2 = zip(range(len(energy)), energy, intensity, background, label)
                for ind_a, single_e, single_i, single_b, single_l in z2:

                    if groups > 1:
                        group_name = self.tableGroups.item(ind, 3).text()
                        single_l = '[{}]:  {}'.format(group_name, single_l)

                    if subtract_background:

                        sub = single_i - single_b

                        if normalize:
                            sub, _ = nmath.normalize_curve(single_e, sub, [w0, w1])

                        if com_shift:
                            if sum([ind, ind_s, ind_a]) == 0:
                                com = nmath.calculateCOM(single_e, sub)
                            else:
                                shift     = nmath.calculateCOM(single_e, sub) - com
                                single_e -= shift


                        self.plotWidget.plot(single_e, sub,
                            pen = pens[ind_s, ind_a], name = single_l)

                    else:

                        if normalize:
                            single_i, fac = nmath.normalize_curve(single_e, single_i, [w0, w1])
                        else:
                            fac = 1.0

                        if com_shift:
                            if sum([ind, ind_s, ind_a]) == 0:
                                com = nmath.calculateCOM(single_e, single_i)
                            else:
                                shift = nmath.calculateCOM(single_e, single_i) - com
                                single_e -= shift

                        self.plotWidget.plot(single_e, single_i, name = single_l,
                            pen = pens[ind_s, ind_a])

                        self.plotWidget.plot(single_e, single_b * fac,
                            pen = pens_bg[ind_s, ind_a])



                    if self.analysis_checkBox_doDifference.isChecked() and ind != 0:
                        single_ref_e = ref_e[ind_s][ind_a]
                        single_ref_i = ref_i[ind_s][ind_a]
                        single_ref_b = ref_b[ind_s][ind_a]

                        i_test      = single_i - single_b
                        i_test_ref  = single_ref_i - single_ref_b
                        i_test,_      = nmath.normalize_curve(single_e, i_test, [w0, w1])
                        i_test_ref,_  = nmath.normalize_curve(single_ref_e, i_test_ref, [w0, w1])

                        de, di, db = nmath.interpolate_and_sum(
                            [single_e, single_ref_e],
                            [single_i, -1 * single_ref_i],
                            [single_b, -1 * single_ref_b], True, [w0, w1])

                        self.plotWidgetDiff.plot(de, di,
                            pen = pens[ind_s, ind_a], name = single_l)

        self.applySettings()



    def _get_pens(self, e, i, b, single_analyzers, single_scans, groups):
        no_scans = len(e)
        no_analyzers = len(e[0])

        pens    = []
        pens_bg = []

        if groups > 1:
            shades = cm.brg(np.linspace(0,1.0, groups))

            pen     = []
            pen_bg  = []
            for ind_g in range(groups):
                c = QtGui.QColor(*shades[ind_g]*255)
                pen.append(pg.mkPen(color=c, style=QtCore.Qt.SolidLine))
                pen_bg.append(pg.mkPen(color=c, style=QtCore.Qt.DashLine))
            pens       = np.tile(pen, (no_scans, no_analyzers, 1))
            pens        = np.transpose(pens, (2,0,1))
            pens_bg    = np.tile(pen_bg, (no_scans, no_analyzers, 1))
            pens_bg     = np.transpose(pens_bg, (2,0,1))


        else:

            if single_analyzers and single_scans:
                shades = cm.brg(np.linspace(0,1.0, no_scans))
                colors = np.tile(shades, (no_analyzers, 1, 1))
                colors = np.transpose(colors, (1,0,2))

            elif single_analyzers and not single_scans:
                shades = cm.brg(np.linspace(0, 1.0, no_analyzers))
                colors = np.tile(shades, (1,1,1))

            elif not single_analyzers and single_scans:
                shades = cm.brg(np.linspace(0,1.0, no_scans))
                colors = np.tile(shades, (1, 1, 1))
                colors = np.transpose(colors, (1,0,2))

            else:
                shades = cm.brg(np.linspace(0,1.0, 1))
                colors = np.tile(shades, (1,1,1))

            for ind_s, scan in enumerate(e):
                pens_scan = []
                pens_scan_bg = []
                for ind_a, analyzer in enumerate(scan):
                    c = QtGui.QColor(*colors[ind_s, ind_a]*255)
                    pens_scan.append(pg.mkPen(color=c, style=QtCore.Qt.SolidLine))
                    pens_scan_bg.append(pg.mkPen(color=c, style=QtCore.Qt.DashLine))
                pens.append(pens_scan)
                pens_bg.append(pens_scan_bg)

        return np.array(pens), np.array(pens_bg)


    def _get_background_pen(self, color):
        pen = pg.mkPen(color=color, style=QtCore.Qt.DashLine)
        return pen


    def clear_plot(self):
        pi = self.plotWidget.getPlotItem()
        items = pi.listDataItems()

        for item in items:
            pi.legend.removeItem(item.name())
            pi.removeItem(item)

        pi = self.plotWidgetDiff.getPlotItem()
        items = pi.listDataItems()

        for item in items:
            pi.legend.removeItem(item.name())
            pi.removeItem(item)

        pi = self.plotWidgetIAD.getPlotItem()
        items = pi.listDataItems()

        for item in items:
            pi.removeItem(item)


    def updateCursorPlot(self, plotWidget, event):
        pos = event[0]
        x = plotWidget.getPlotItem().vb.mapSceneToView(pos).x()
        y = plotWidget.getPlotItem().vb.mapSceneToView(pos).y()
        fmt = 'x: {:.7f} | y: {:.7f}'.format(x,y)
        self.statusBar.writeCursorPosition(fmt)
