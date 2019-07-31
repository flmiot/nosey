import time
import numpy as np
import nosey

from nosey.analysis.result import AnalysisResult

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
        self.bg_roi                 = [] # List of tuples of bg ROI



    def get_spectrum(self):

        """
        """

        start = time.time()

        if len(self.scans) < 1:
            raise ValueError("No active scans!")
        if len(self.analyzers) < 1:
            raise ValueError("No active analyzers!")

        types = list([(s.name,'{}f4'.format(len(s.images))) for s in self.scans])


        result = AnalysisResult()

        for scan in self.scans:

            in_e, out_e, inte, back, fit = scan.get_energy_spectrum(self.analyzers,
                self.bg_roi)

            d = {scan.name : list([a.name for a in self.analyzers])}
            result.add_data(in_e, out_e, inte, back, fit, d)

        end = time.time()
        fmt = "Single spectra obtained [Took {:2f} s]".format(end-start)
        nosey.Log.debug(fmt)
        start = end


        end = time.time()
        fmt = "Spectra summed [Took {:2f} s]".format(end-start)
        nosey.Log.debug(fmt)



        return result
