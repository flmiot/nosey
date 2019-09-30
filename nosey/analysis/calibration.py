import numpy as np

class EnergyCalibration(object):
    def __init__(self, positions, energies):
        self.pos = positions
        self.energies = energies

    def getAxis(self, x):
        if len(self.pos) < 3:
            fitting_degree = 1
        else:
            fitting_degree = 3
        coeff = np.polyfit(self.pos, self.energies, fitting_degree)
        return np.poly1d(coeff)(x), None
