import numpy as np
import nosey

from nosey.guard import timer
from nosey.analysis.result import AnalysisResult

class Experiment(object):
    """ An Experiment holds a set of analyzers for a number of scans.
    """

    def __init__(self):
        self.scans                  = []
        self.analyzers              = []


    @timer("Analysis finished")
    def get_spectrum(self):

        """
        """

        if len(self.scans) < 1:
            raise ValueError("No active scans!")
        if len(self.analyzers) < 1:
            raise ValueError("No active analyzers!")

        types = list([(s.name,'{}f4'.format(len(s.images))) for s in self.scans])

        result = AnalysisResult()

        for scan in self.scans:

            in_e, out_e, inte, back, fit = scan.get_energy_spectrum(self.analyzers)

            d = {scan.name : list([a.name for a in self.analyzers])}
            result.add_data(in_e, out_e, inte, back, fit, d)

        print("Hi!")


        return result
