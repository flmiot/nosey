import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui

class ROI(object):
    def __init__(self, position, size, name):
        self.active     = True
        self.name       = name

        self.objects        = []
        self.b1_distance    = 0
        self.b2_distance    = 0

        # ROI Pens
        signal_pen = pg.mkPen(color='#e5ff00')
        bg_pen = pg.mkPen(color='#696969', style=QtCore.Qt.DashLine)
        axis_pen = pg.mkPen(color='#2b573e', style=QtCore.Qt.DotLine)

        # Component ROI
        signal         = pg.ROI(position, size, pen = signal_pen)
        signal.addScaleHandle([0.5, 1], [0.5, 0])
        signal.addScaleHandle([0.5, 0], [0.5, 1])
        signal.addScaleHandle([0, 0.5], [1, 0.5])
        signal.addScaleHandle([1, 0.5], [0, 0.5])
        pos = [position[0], position[1] + size[1] / 2]
        axis = pg.ROI(pos, [size[0], 0], pen = axis_pen)
        size[1] = size[1] * 0.5
        background01   = pg.ROI(position, size, pen = bg_pen)
        background01.addScaleHandle([0.5, 0], [0.5, 1])
        background02   = pg.ROI(position, size,  pen = bg_pen)
        background02.addScaleHandle([0.5, 1], [0.5, 0])

        self.objects.extend([signal, background01, background02, axis])

        pos_b1, pos_b2 = self._calculateBackgroundPosition()
        background01.setPos(position[0], pos_b1)
        background02.setPos(position[0], pos_b2)

        # Connect events
        for object in self.objects:
            object.sigRegionChanged.connect(self.regionChanged)


    def toggle(self):
        self.active = not self.active


    def addToMonitor(self, monitor):
        for object in self.objects:
            monitor.imageView.getView().addItem(object)
            if isinstance(object, pg.LineSegmentROI):
                for handle in object.getHandles():
                    object.removeHandle(handle)

    def removeFromMonitor(self, monitor):
        for object in self.objects:
            monitor.imageView.getView().removeItem(object)


    def regionChanged(self, object):
        for obj in self.objects:
            obj.sigRegionChanged.disconnect(self.regionChanged)

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

            # Update all object sizes
            b1.setSize([size[0], b1.size()[1]])
            b2.setSize([size[0], b2.size()[1]])

        if object in self.objects[1:3]:
            pos         = self.objects[0].pos()
            pos_object  = object.pos()

            if object == self.objects[1]:
                self.b1_distance = self._calculateBackgroundDistance()[0]
                b1_pos = self._calculateBackgroundPosition()[0]
                object.setPos(pos[0], b1_pos)

            if object == self.objects[2]:
                self.b2_distance = self._calculateBackgroundDistance()[1]
                b2_pos = self._calculateBackgroundPosition()[1]
                object.setPos(pos[0], b2_pos)

        for obj in self.objects:
            obj.sigRegionChanged.connect(self.regionChanged)


    def _calculateBackgroundDistance(self):
        position    = self.objects[0].pos()
        size        = self.objects[0].size()
        b1, b2      = self.objects[1:3]
        b1_distance = max(0, position[1] - b1.pos()[1] - b1.size()[1])
        b2_distance = max(0, b2.pos()[1] - position[1] - size[1])
        return b1_distance, b2_distance


    def _calculateBackgroundPosition(self):
        position    = self.objects[0].pos()
        size        = self.objects[0].size()
        b1, b2 = self.objects[1:3]
        pos_b1 = position[1] - self.b1_distance - b1.size()[1]
        pos_b2 = position[1] + size[1] + self.b2_distance
        return pos_b1, pos_b2
