import numpy as np
import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui

import nosey
from nosey.analysis.analyzer import Analyzer
import nosey.analysis.math as nmath
import matplotlib.pyplot as plt


class ROI(object):

    def __init__(self, position, size, name):
        super().__init__()
        self.active = True
        self.objects = []
        self.energyPoints = []
        self.b1_distance = 0
        self.b2_distance = 0

        self.proxies = []

        # ROI Pens
        signal_pen = pg.mkPen(color='#e5ff00')
        bg_pen = pg.mkPen(color='#44c964', style=QtCore.Qt.DashLine)
        axis_pen = pg.mkPen(color='#2b573e', style=QtCore.Qt.DotLine)

        # Component ROI
        signal = pg.ROI(position, size, pen=signal_pen)
        signal.addScaleHandle([0.5, 1], [0.5, 0])
        signal.addScaleHandle([0.5, 0], [0.5, 1])
        signal.addScaleHandle([0, 0.5], [1, 0.5])
        signal.addScaleHandle([1, 0.5], [0, 0.5])
        pos = [position[0], position[1] + size[1] / 2]
        axis = pg.ROI(pos, [size[0], 0], pen=axis_pen)
        size[1] = size[1] * 0.5
        background01 = pg.ROI(position, size, pen=bg_pen)
        background01.addScaleHandle([0.5, 0], [0.5, 1])
        background02 = pg.ROI(position, size, pen=bg_pen)
        background02.addScaleHandle([0.5, 1], [0.5, 0])

        self.objects.extend([signal, background01, background02, axis])

        pos_b1, pos_b2 = self._calculateBackgroundPosition()
        background01.setPos(position[0], pos_b1)
        background02.setPos(position[0], pos_b2)
        self.changeName(name)

        self.connectUpdateSlot(self.regionChanged)

    def connectUpdateSlotProxy(self, slot):
        self.proxies.clear()

        for obj in self.objects:
            proxy = pg.SignalProxy(obj.sigRegionChanged,
                                   delay=nosey.lastComputationTime, slot=slot)
            self.proxies.append(proxy)

        for obj in self.energyPoints:
            proxy = pg.SignalProxy(obj.sigRegionChanged,
                                   delay=nosey.lastComputationTime, slot=slot)
            self.proxies.append(proxy)

    def connectUpdateSlot(self, slot):
        for obj in self.objects:
            obj.sigRegionChanged.connect(slot)

        for obj in self.energyPoints:
            obj.sigRegionChanged.connect(slot)

    def blockSignals(self, b):
        for obj in self.objects:
            obj.blockSignals(b)

        for obj in self.energyPoints:
            obj.blockSignals(b)

    def getCoordinates(self, imageView):
        if imageView.image is None:
            return

        image = imageView.getProcessedImage()

        # Extract image data from ROI
        axes = (imageView.axes['x'], imageView.axes['y'])

        coordinates = []
        for object in self.objects[:3]:
            _, coords = object.getArrayRegion(image.view(
                np.ndarray), imageView.imageItem, axes, returnMappedCoords=True)

            if coords is None:
                coordinates.append(None)
                continue

            # get bounding box
            x, y = coords[0].flatten(), coords[1].flatten()

            x0, x1 = np.min(x), np.max(x)
            y0, y1 = np.min(y), np.max(y)
            bbox = list([int(i) for i in [x0, y0, x1, y1]])
            coordinates.append(bbox)

        return coordinates

    def toggle(self):
        self.active = not self.active

    def changeName(self, name):
        self.name = name
        self.objects[0].setToolTip(self.name)

    def addToMonitor(self, monitor):
        for object in self.objects:
            monitor.imageView.getView().addItem(object)
            if isinstance(object, pg.LineSegmentROI):
                for handle in object.getHandles():
                    object.removeHandle(handle)

    def removeFromMonitor(self, monitor):
        for object in self.objects:
            monitor.imageView.getView().removeItem(object)

        for energyPoint in self.energyPoints:
            monitor.imageView.getView().removeItem(energyPoint)

    def addEnergyPoint(self, x, monitor):
        ep_pen = pg.mkPen(color='#ff6666')
        y = self.objects[0].pos()[1] + self.objects[0].size()[1] / 2
        name = '{} - Index: {}'.format(self.name, len(self.energyPoints))
        c = EnergyPointROI([x, y], size=(10, 10), name=name, pen=ep_pen)
        self.energyPoints.append(c)
        monitor.imageView.getView().addItem(c)

        # Event handling
        c.sigRegionChanged.connect(self.regionChanged)

    def removeEnergyPoint(self, index, monitor):
        try:
            c = self.energyPoints[index]
            monitor.imageView.getView().removeItem(c)
            self.energyPoints.remove(c)
        except Exception as e:
            nosey.Log.error(
                "Energy point removal skipped for roi {}".format(self))

    def clearEnergyPoints(self, monitor):
        for index in range(len(self.energyPoints)):
            self.removeEnergyPoint(0, monitor)

    def getEnergyPointPositions(self):
        positions = []
        for ep in self.energyPoints:
            pos = ep.pos()[0]
            positions.append(pos)

        return positions

    def setEnergyPointsAuto(self, images, imageView, sum_before_detection,
                            search_radius):
        sig = Analyzer.make_signal_from_QtRoi(self, [195, 487], imageView, 0)
        bg01 = Analyzer.make_signal_from_QtRoi(self, [195, 487], imageView, 1)
        bg02 = Analyzer.make_signal_from_QtRoi(self, [195, 487], imageView, 2)
        positions = np.empty(len(self.energyPoints))
        self.blockSignals(True)

        if sum_before_detection:
            image = np.sum(images, axis=0)
            x, y, bg, _ = sig.get_signal_series([image], bg01, bg02)
            y -= bg
            x = x[0]
            curve = np.ma.array(y[0], mask=False)

            # Find peaks with search_radius
            peaks = []
            for n in range(len(self.energyPoints)):
                max_index = curve.argmax()
                i0 = max(0, max_index - search_radius)
                i1 = min(max_index + search_radius, len(curve))
                x_com = np.arange(len(curve))
                pos = nmath.calculateCOM(x_com, curve, window=[i0, i1])
                peaks.append(pos)
                new_mask = curve.mask
                new_mask[int(pos - search_radius)
                             :int(pos + search_radius)] = True
                curve.mask = new_mask

            peaks = sorted(peaks)

            for ind, peak_pos in enumerate(peaks):
                object = self.energyPoints[ind]
                ep_pos = object.pos()
                ep_pos[0] = peak_pos + sig.get_roi()[0]
                object.setPos(ep_pos)

        else:
            if images.shape[0] != len(self.energyPoints):
                self.blockSignals(False)
                fmt = "Unequal number of energy points and runs. "\
                    "Enable 'Sum runs before search'."
                raise IndexError(fmt)

            x, y, bg, _ = sig.get_signal_series(images, bg01, bg02)
            y -= bg

            for ind, curve in enumerate(y):
                object = self.energyPoints[ind]
                ep_pos = object.pos()
                max_index = np.argmax(curve)
                x_com = np.arange(len(curve))
                i0, i1 = max_index - search_radius, max_index + search_radius
                ep_pos[0] = nmath.calculateCOM(x_com, curve, window=[i0, i1])
                ep_pos[0] += sig.get_roi()[0]
                object.setPos(ep_pos)

        self.blockSignals(False)

    def regionChanged(self, object):

        self.blockSignals(True)

        if object == self.objects[0]:

            pos = object.pos()
            size = object.size()

            # Update all object positions
            b1, b2 = self.objects[1:3]
            b1_pos, b2_pos = self._calculateBackgroundPosition()
            b1.setPos(pos[0], b1_pos)
            b2.setPos(pos[0], b2_pos)

            axis = self.objects[3]
            axis.setPos([0, pos[1] + size[1] / 2])

            for energyPoint in self.energyPoints:
                ep_pos = energyPoint.pos()
                ep_pos[1] = pos[1] + size[1] / 2
                energyPoint.setPos(ep_pos)

            # Update all object sizes
            b1.setSize([size[0], b1.size()[1]])
            b2.setSize([size[0], b2.size()[1]])

        if object in self.objects[1:3]:
            pos = self.objects[0].pos()
            pos_object = object.pos()

            if object == self.objects[1]:
                self.b1_distance = self._calculateBackgroundDistance()[0]
                b1_pos = self._calculateBackgroundPosition()[0]
                object.setPos(pos[0], b1_pos)

            if object == self.objects[2]:
                self.b2_distance = self._calculateBackgroundDistance()[1]
                b2_pos = self._calculateBackgroundPosition()[1]
                object.setPos(pos[0], b2_pos)

        if object in self.energyPoints:
            pos, size = self.objects[0].pos(), self.objects[0].size()
            ep_pos = object.pos()
            ep_pos[1] = pos[1] + size[1] / 2
            object.setPos(ep_pos)

        self.blockSignals(False)

    def _calculateBackgroundDistance(self):
        position = self.objects[0].pos()
        size = self.objects[0].size()
        b1, b2 = self.objects[1:3]
        b1_distance = max(0, position[1] - b1.pos()[1] - b1.size()[1])
        b2_distance = max(0, b2.pos()[1] - position[1] - size[1])
        return b1_distance, b2_distance

    def _calculateBackgroundPosition(self):
        position = self.objects[0].pos()
        size = self.objects[0].size()
        b1, b2 = self.objects[1:3]
        pos_b1 = position[1] - self.b1_distance - b1.size()[1]
        pos_b2 = position[1] + size[1] + self.b2_distance
        return pos_b1, pos_b2


class EnergyPointROI(pg.ROI):
    def __init__(self, pos, size, name, **args):
        self.path = None
        pg.ROI.__init__(self, pos, size, **args)
        self.sigRegionChanged.connect(self._clearPath)
        self.setToolTip(name)
        # self._addHandles()

    def _clearPath(self):
        self.path = None

    def paint(self, p, opt, widget):
        r = self.boundingRect()
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        p.setPen(self.currentPen)
        p.scale(r.width(), r.height())  # workaround for GL bug
        r = QtCore.QRectF(-.5, -.5, 1, 1)

        p.drawEllipse(r)
        p.drawLine(QtCore.QPointF(0, -.5), QtCore.QPointF(0, .5))

    def boundingRect(self):
        r = pg.ROI.boundingRect(self)
        size = r.width()
        radius = size / 2
        return QtCore.QRectF(r.x() - radius, r.y() - radius, size, size)

    def getArrayRegion(self, arr, img=None, axes=(0, 1), **kwds):
        """
        Return the result of ROI.getArrayRegion() masked by the elliptical shape
        of the ROI. Regions outside the ellipse are set to 0.
        """
        # Note: we could use the same method as used by PolyLineROI, but this
        # implementation produces a nicer mask.
        arr = ROI.getArrayRegion(self, arr, img, axes, **kwds)
        if arr is None or arr.shape[axes[0]] == 0 or arr.shape[axes[1]] == 0:
            return arr
        w = arr.shape[axes[0]]
        h = arr.shape[axes[1]]

        # generate an ellipsoidal mask
        mask = np.fromfunction(lambda x, y: (
            ((x + 0.5) / (w / 2.) - 1)**2 + ((y + 0.5) / (h / 2.) - 1)**2)**0.5 < 1, (w, h))

        # reshape to match array axes
        if axes[0] > axes[1]:
            mask = mask.T
        shape = [(n if i in axes else 1) for i, n in enumerate(arr.shape)]
        mask = mask.reshape(shape)

        return arr * mask

    def shape(self):
        if self.path is None:
            path = QtGui.QPainterPath()

            # Note: Qt has a bug where very small ellipses (radius <0.001) do
            # not correctly intersect with mouse position (upper-left and
            # lower-right quadrants are not clickable).
            # path.addEllipse(self.boundingRect())

            # Workaround: manually draw the path.
            br = self.boundingRect()
            center = br.center()
            r1 = br.width() / 2.
            r2 = br.height() / 2.
            theta = np.linspace(0, 2 * np.pi, 24)
            x = center.x() + r1 * np.cos(theta)
            y = center.y() + r2 * np.sin(theta)
            path.moveTo(x[0], y[0])
            for i in range(1, len(x)):
                path.lineTo(x[i], y[i])
            self.path = path

        return self.path
