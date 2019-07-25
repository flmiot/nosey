import time
import logging
import numpy as np
import logging
import nosey

from nosey.analysis.calibration import EnergyCalibration

Log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class Analyzer(object):
    def __init__(self, name, roi = None, mask = None):
        """
        Analyzers have a
        property called *active*, which can be used to include/exclude them when
        doing summed signal analysis.
        """

        self.roi                = None      # xmin,ymin,xmax,ymax e.g. [0,0,5,5]
        self.active             = True
        self.name               = name
        self.mask               = None
        self.poly_fit           = False
        self.poly_order         = 6
        self.calibration        = None

        if roi is not None:
            self.set_roi(roi)

        if mask is not None:
            self.set_mask(mask)

    @classmethod
    def make_signal_from_QtRoi(cls, roi, mask, imageView, type = 0):
        """type can be 0,1 or 2 (signal, bg01 or bg02)"""
        bb = roi.getCoordinates(imageView)[type]
        a = cls(roi.name)
        a.set_roi(bb)
        a.set_mask(mask)

        return a


    def size(self, mask = None):
        if mask is None:
            x0, y0, x1, y1 = self.roi
        else:
            x0, y0, x1, y1 = self.clip_roi(self.roi, mask)

        size = y1 - y0 + 1
        return size if size > 0 else 0


    def pos(self):
        x0, y0, x1, y1 = self.roi
        return np.array([(y1-y0)/2 + y0, (x1-x0)/2 + x0])


    def set_roi(self, roi):

        if isinstance(roi, list):
            self.roi = np.array(roi)
        elif isinstance(roi, np.ndarray):
            self.roi = roi
        else:
            fmt = "ROI has to be specified like [xmin, ymin, xmax, ymax], "\
                "either as list or np.ndarray."
            raise Exception(fmt)


    def get_roi(self, mask = None):

        if mask is None:
            mask = self.mask

        if mask is None:
            return self.roi
        else:
            return self.clip_roi(self.roi, mask)


    def set_mask(self, mask):
        if isinstance(mask, list):
            self.mask = np.array(mask)
        elif isinstance(mask, np.ndarray):
            self.mask = mask
        else:
            fmt = "Mask has to be specified like [ymax, xmax], "\
                "either as list or np.ndarray."
            raise Exception(fmt)


    def setEnergies(self, positions, energies):
        self.calibration = EnergyCalibration(positions, energies)


    def get_signal(self, image, poly_fit = False, poly_order = 6):
        """
        """

        if self.roi is None:
            raise ValueError("ROI needs to be set before use.")

        x0,y0,x1,y1 = self.clip_roi(self.roi, image.shape)

        ii = np.sum(image[y0:y1+1,x0:x1+1], axis = 0)
        ea = np.arange(len(ii))

        if poly_fit:
            p = np.polyfit(ea, ii, poly_order)
            poly = np.poly1d(p)
            ii = poly(ea)

        return ea, ii


    def get_signal_series(self, images, background_rois = None):
        """

        """

        start = time.time()
        x0, y0, x1, y1 = self.clip_roi(self.roi, images[0].shape)

        if self.calibration is None:
            ea = np.arange(len(np.arange(x0, x1+1)))
            fit = None
        else:
            ea, fit = self.calibration.getAxis(np.arange(len(np.arange(x0, x1+1))))

        ii = np.empty(len(images), dtype = list)
        bg = np.zeros(len(images), dtype = list)


        for ind, image in enumerate(images):
            _, ii[ind] = self.get_signal(image)
            bg[ind] = self.get_background(image, background_rois)



        end = time.time()
        fmt = "Returned signal series [Took {:2f} s]".format(end-start)
        Log.debug(fmt)

        return ea, ii, bg, fit

    def clip_roi(self, roi, shape):
        x0, y0, x1, y1 = roi

        if x0 < 0:
            x0 = 0
        if y0 < 0:
            y0 = 0
        if x1 > shape[1] - 1:
            x1 = shape[1] - 1
        if y1 > shape[0] - 1:
            y1 = shape[0] - 1

        return [x0,y0,x1,y1]


    def get_background(self, image, background_rois):

        bg = np.zeros(image.shape[1])

        upper = None
        lower = None

        # Find nearest background ROIs
        for bg_roi in background_rois:
            if bg_roi.pos()[0] > self.pos()[0]:
                if upper is None:
                    upper = bg_roi
                else:
                    dis_self_roi = np.linalg.norm(self.pos() - bg_roi.pos())
                    dis_self_upper = np.linalg.norm(self.pos() - upper.pos())
                    if dis_self_roi < dis_self_upper:
                        upper = bg_roi
            else:
                if lower is None:
                    lower = bg_roi
                else:
                    dis_self_roi = np.linalg.norm(self.pos() - bg_roi.pos())
                    dis_self_lower = np.linalg.norm(self.pos() - lower.pos())
                    if dis_self_roi < dis_self_lower:
                        lower = bg_roi

        if not upper is None:
            #x0, y0, x1, y1 = self.clip_roi(upper.roi, image.shape)
            #bg_upper = np.sum(image[y0:y1+1, x0:x1+1], axis = 0)
            _, bg_upper = upper.get_signal(image, poly_fit = upper.poly_fit,
                poly_order = upper.poly_order)
            size = upper.size(mask = image.shape)
            if size > 0:
                x0, _, x1, _ = upper.clip_roi(upper.roi, image.shape)
                bg[x0:x1+1] += bg_upper * self.size(mask = image.shape) / size
            else:
                upper = None

        if not lower is None:
            #x0, y0, x1, y1 = self.clip_roi(lower.roi, image.shape)
            #bg_lower = np.sum(image[y0:y1+1, x0:x1+1], axis = 0)
            _, bg_lower = lower.get_signal(image, poly_fit = lower.poly_fit,
                poly_order = lower.poly_order)
            size = lower.size(mask = image.shape)
            if size > 0:
                x0, _, x1, _ = lower.clip_roi(lower.roi, image.shape)
                bg[x0:x1+1] += bg_lower * self.size(mask = image.shape) / size
            else:
                lower = None

        if not lower is None and not upper is None:
            bg /= 2

        x0, _, x1, _ = self.clip_roi(self.roi, image.shape)
        # plt.plot(bg)
        # plt.show()
        return bg[x0:x1+1]
