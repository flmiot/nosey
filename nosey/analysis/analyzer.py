import time
import numpy as np
import nosey
import nosey.analysis.math as nmath
from nosey.analysis.calibration import EnergyCalibration
from nosey.guard import timer


class Analyzer(object):
    def __init__(self, name, rois = None, mask = None, calibration = None):
        self.name               = name
        self.rois               = {'signal': [], 'upper_bg': [], 'lower_bg': []}
        self.mask               = None
        self.calibration        = None

        if rois is not None:
            self.rois = rois

        if mask is not None:
            self.mask = mask

        if calibration is not None:
            self.calibration = calibration


    @classmethod
    def make_signal_from_QtRoi(cls, roi, mask, imageView, type = 0):
        """type can be 0,1 or 2 (signal, bg01 or bg02)"""
        bb = roi.getCoordinates(imageView)[type]
        a = cls(roi.name)
        a.set_roi(bb)
        a.set_mask(mask)

        return a


    @timer("Return integrated counts for analyzer")
    def counts(self, images, axis_calibration = True):
        """ Integrate a region of interest (ROI) for this analyzer.

        Dimensions:
        -----------
        N: Number of detector images
        x: Number of detector pixels along primary axis
        y: Number of detector pixels along secondary axis

        Args:
            images  (np.ndarray)
                    array of detector images with shape (N, y, x)
            r_type  (string)
                    ROI type, either "signal", "upper_bg" or "lower_bg"

        Raises:
            ValueError: Invalid image input array, invalid type string or ROI

        Returns:
            (np.ndarray) Integrated detector images with shape (N, x)
        """

        # Counts
        try:
            ii          = self.integrate(images, 'signal')
            size        = self.size('signal')
            bg_rois     = 0
        except ValueError as e:
            fmt = "Please set a valid signal ROI before use: {}".format(e)
            raise ValueError(fmt)

        try:
            bg_upper    = self.integrate(images, 'upper_bg')
            bg_upper   *= size / self.size('upper_bg')
            bg_rois    += 1
        except:
            bg_upper    = np.zeros((images.shape[0], ii.shape[1] ))

        try:
            bg_lower    = self.integrate(images, 'lower_bg')
            bg_lower   *= size / self.size('lower_bg')
            bg_rois    += 1
        except:
            bg_lower    = np.zeros((images.shape[0], ii.shape[1] ))

        if bg_rois > 0:
            bg = (bg_upper + bg_lower) / bg_rois
        else:
            bg = np.zeros((images.shape[0], ii.shape[1] ))

        # Axis calibration
        if axis_calibration:
            x0, _, x1, _ = self.get_roi('signal')
            try:
                ea, fit = self.calibration.getAxis(np.arange(x0, x1))
            except:
                # Non calibrated axes always start with 0 to let users shift
                # uncalibrated curves by moving the signal region of interest
                # (ROI)
                ea, fit = np.arange(x0, x1) - x0, None
        else:
            ea, fit = None, None



        return ea, ii, bg, fit


    def integrate(self, images, r_type):
        """ Integrate a region of interest (ROI) for this analyzer.

        Dimensions:
        -----------
        N: Number of detector images
        x: Number of detector pixels along primary axis
        y: Number of detector pixels along secondary axis

        Args:
            images  (np.ndarray)
                    array of detector images with shape (N, y, x)
            r_type  (string)
                    ROI type, either "signal", "upper_bg" or "lower_bg"

        Raises:
            ValueError: Invalid image input array, invalid type string or ROI

        Returns:
            (np.ndarray) Integrated detector images with shape (N, 1, x)
        """

        x0, y0, x1, y1 = self.get_roi(r_type)
        return np.sum(images[:, y0:y1+1, x0:x1+1], axis = 1)


    def set_roi(self, roi, r_type):
        """ Set region of interest (ROI) coordinates for this analyzer.

        Args:
            roi     (list)
                    ROI coordinates as [x0, y0, x1, y1]
            r_type  (string)
                    ROI type, either "signal", "upper_bg" or "lower_bg"

        Raises:
            ValueError: Wrong coordinate format or invalid type string

        Returns:
            None
        """

        if not r_type in self.rois.keys():
            raise ValueError('Invalid roi type requested: {}'.format(r_type))

        if isinstance(roi, list) and len(roi) == 4:
            self.rois[r_type] = roi
        else:
            raise ValueError('Invalid ROI coordinate format: {}'.format(roi))


    def get_roi(self, r_type, mask = None):
        """ Get region of interest (ROI) coordinates from this analyzer.

        Args:
            type    (string)
                    ROI type, either "signal", "upper_bg" or "lower_bg"
            r_type  (tuple)
                    2D image shape used for clipping, i.e. (dim1, dim2)

        Raises:
            ValueError: Invalid type string, invalid ROI

        Returns:
            (list) roi coordinates as [x0, y0, x1, y1]
        """

        if not r_type in self.rois.keys():
            raise ValueError('Invalid ROI type requested: {}'.format(r_type))

        if mask is None:
            mask = self.mask

        return self.clip_roi(self.rois[r_type], mask)


    def calibrate(self, positions, energies):
        """ Add an energy calibration to this analyzer.

        Args:
            positions   (list) 1D positions along the dispersive detector axis
            energies    (list) corresponding energies for positions

        Raises:
            -

        Returns:
            None
        """

        self.calibration = EnergyCalibration(positions, energies)


    def auto_calibrate(self, images, energies, sum_before, search_radius,
        outlier_rejection = False):
        """ Add an energy calibration to this analyzer automatically.

        Dimensions:
        -----------
        N: Number of detector images
        x: Number of detector pixels along primary axis
        y: Number of detector pixels along secondary axis

        Args:
            images              (np.ndarray)
                                array of detector images with shape (N, y, x)
            energies            (list)
                                Calibration energies (will also determine how
                                many peaks are searched)
            sum_before          (bool)
                                sum images before peak search
            search_radius       (int)
                                search radius for peak detection
            outlier_rejection   (bool)
                                Suppress single pixel intensity outliers during
                                peak search

        Raises:
            ValueError:
                                Invalid detector image input array
            IndexError:
                                Unequal number of images and energies

        Returns:
            None
        """

        _, ii, bg, _ = self.counts(images, axis_calibration = False)
        peaks = []

        if outlier_rejection:
            outliers = nmath.getOutliers(np.sum(images, axis = 0))
            outliers = [x[0] for x in outliers]

        if sum_before:  # Number of images and len(energies) can be different

            ii = np.sum(ii, axis = 0) - np.sum(bg, axis = 0)
            curve = np.ma.array(ii , mask = False)

            # Find len(energies) peaks with *search_radius*
            for n in range( len(energies) ):
                max_index = curve.argmax()

                if outlier_rejection:
                    while max_index in outliers:
                        new_mask = curve.mask
                        new_mask[max_index] = True
                        curve.mask = new_mask
                        max_index = curve.argmax()

                i0 = max(0, max_index - search_radius)
                i1 = min(max_index + search_radius, len(curve))
                x_com = np.arange(len(curve))
                pos = nmath.calculateCOM(x_com, curve, window = [i0, i1])
                pos += self.get_roi('signal')[0]
                peaks.append(pos)
                new_mask = curve.mask
                new_mask[int(pos-search_radius):int(pos+search_radius)] = True
                curve.mask = new_mask

        else:  # There has to be one image for each energy in *energies*

            if images.shape[0] != len( energies ):
                fmt = "Unequal number of energy points and runs. "\
                "Enable 'Sum runs before search'."
                raise IndexError(fmt)

            ii -= bg

            for ind, curve in enumerate(ii):
                max_index = np.argmax(curve)
                x_com = np.arange(len(curve))
                i0, i1 = max_index - search_radius, max_index + search_radius
                pos = nmath.calculateCOM(x_com, curve, window = [i0, i1])
                pos += self.get_roi('signal')[0]
                peaks.append(pos)

        peaks = sorted(peaks)
        self.calibrate(peaks, energies)



    def size(self, r_type, mask = None):
        """ Get the size of the regions of interest (ROI) for this analyzer.

        Args:
            r_type  (string)
                    ROI type, either "signal", "upper_bg" or "lower_bg"
            mask    (tuple)
                    2D image shape used for clipping, i.e. (dim1, dim2)

        Raises:
            ValueError: Invalid type string

        Returns:
            (tuple) Size for requested ROI type in pixels
        """

        if not r_type in self.rois.keys():
            raise ValueError('Invalid ROI type requested: {}'.format(r_type))

        if mask is None:
            mask = self.mask

        x0, y0, x1, y1 = self.clip_roi(self.rois[r_type], mask)
        size = (x1 - x0 if x1 - x0 > 0 else 0, y1 - y0 if y1 - y0 > 0 else 0)
        return size


    def pos(self):
        """ Get the position of the 'signal' region of interest (ROI).

        Args:
            mask    (tuple)
                    2D image shape used for clipping, i.e. (dim1, dim2)

        Raises:
            -

        Returns:
            (tuple) Position in pixels
        """
        x0, y0, x1, y1 = self.rois['signal']
        pos = tuple((y1-y0)/2 + y0, (x1-x0)/2 + x0)
        return pos


    def clip_roi(self, coordinates, shape = None):
        """ Clip region of interest (ROI) coordinates with an image shape.

        Args:
            coordinates (list) list of ROI coordinates
            shape       (tuple) image shape used for clipping

        Raises:
            ValueError: Invalid coordinate format, invalid shape

        Returns:
            (list) Clipped ROI coordinates
        """

        if shape is None:
            return coordinates

        if not isinstance(coordinates, list) and len(coordinates) == 4:
            raise ValueError("Invalid ROI coordinate input.")

        x0, y0, x1, y1 = coordinates
        if x0 < 0:
            x0 = 0
        if y0 < 0:
            y0 = 0
        if x1 > shape[1] - 1:
            x1 = shape[1] - 1
        if y1 > shape[0] - 1:
            y1 = shape[0] - 1

        return [x0,y0,x1,y1]
