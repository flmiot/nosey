import numpy as np

class EnergyCalibration(object):
    def __init__(self, positions, energies):
        self.pos = positions
        self.energies = energies

    def getAxis(self, x):
        fitting_degree = 3
        coeff = np.polyfit(self.pos, self.energies, fitting_degree)
        return np.poly1d(coeff)(x), None
