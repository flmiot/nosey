import time
import numpy as np
import logging
import nosey

from nosey.analysis.result import AnalysisResult

Log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class Experiment(object):
    """An Experiment holds a set of analyzers for a number of scans. For each
    scan, summed spectra can be obtained by calling the *get_spectrum()* method.
    The returned spectra can be summed over all active analyzers (property
    'active' of each analyzer). Additionally, all scans can be summed for which
    the 'active' property was set to true (see *Scan* class).
    """

    def __init__(self):
        """Use the *add_scan* method to populate the experiment with scans."""
        self.scans                  = [] # List of all added scans
        self.analyzers              = [] # List of all added anaylzers
        self.bg_rois                = [] # List of all available background ROIs



    def get_spectrum(self):

        """
        """

        start = time.time()
        active_analyzers = list([a for a in self.analyzers if a.active])
        active_background_rois = list([b for b in self.bg_rois if b.active])
        active_scans = list([s for s in self.scans if s.active])

        if len(active_scans) < 1:
            raise ValueError("No active scans!")
        if len(active_analyzers) < 1:
            raise ValueError("No active analyzers!")

        types = list(
            [(s.name,'{}f4'.format(len(s.images))) for s in active_scans])

        # e = []#np.empty(len(active_analyzers), types)
        # i = []#np.empty(len(active_analyzers), types)
        # b = []#np.empty(len(active_analyzers), types)

        result = AnalysisResult()

        for scan in active_scans:

            # index = self.scans.index(scan)

            # # Calibrate analyzers
            # try:
            #     calibration = self.calibrations[index]
            #     calibration.calibrate_energy_for_analyzers(
            #         analyzers = active_analyzers)
            # except Exception as e:
            #     calibration = None
            #     fmt = "Energy calibration for scan {} failed: {}."
            #     Log.error(fmt.format(scan.name, e))

            in_e, out_e, inte, back, fit = scan.get_energy_spectrum(active_analyzers,
                active_background_rois)

            d = {scan.name : list([a.name for a in active_analyzers])}
            result.add_data(in_e, out_e, inte, back, fit, d)

        end = time.time()
        fmt = "Single spectra obtained [Took {:2f} s]".format(end-start)
        Log.debug(fmt)
        start = end


        end = time.time()
        fmt = "Spectra summed [Took {:2f} s]".format(end-start)
        Log.debug(fmt)



        return result


    def add_analyzer(self, analyzer):
        """Add an analyzer object to this experiment. Raise an exception if
        analyzer already exists.
        """

        if analyzer in self.analyzers:
            raise ValueError("Analyzer is already used for this experiment.")

        self.analyzers.append(analyzer)


    def remove_analyzer(self, analyzer):
        """Remove an analyzer from the experiment."""
        if analyzer not in self.analyzers:
            raise ValueError("Analyzer is not known inside this experiment.")

        self.analyzers.remove(analyzer)


    def add_background_roi(self, bg_roi):
        """Add an bg roi object to this experiment. Raise an exception if
        bg roi already exists.
        """

        if bg_roi in self.bg_rois:
            raise ValueError("Background ROI is already used for this experiment.")

        self.bg_rois.append(bg_roi)


    def add_scan(self, scan):
        """Add a scan object. Specify scan."""
        self.scans.append(scan)
