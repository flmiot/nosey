import numpy as np

class EnergyCalibration(object):
    def __init__(self, positions, energies):
        self.pos = positions
        self.energies = energies


    def getAxis(self, x, out = None):
        fitting_degree = 3
        coeff = np.polyfit(self.pos, self.energies, fitting_degree)
        if out is None:
            return np.poly1d(coeff)(x), None
        else:
            out['ea'], out['fit'] = np.poly1d(coeff)(x), None
