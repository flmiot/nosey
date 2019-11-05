"""Analysis result"""

import numpy as np
import scipy.interpolate as interp
import nosey

from nosey.analysis.label import Label
import nosey.analysis.math as nmath

import matplotlib.pyplot as plt


class AnalysisResult(object):
    def __init__(self):
        self.in_e = []
        self.out_e = []
        self.intensities = []
        self.background = []
        self.fits = []
        self.labels = Label()

    def add_data(self, in_e, out_e, intensity, background, fit, label_dict):
        self.in_e.append(in_e)
        self.out_e.append(out_e)
        self.intensities.append(intensity)
        self.background.append(background)
        self.fits.append(fit)
        self.labels.add_scan_labels(label_dict)

    def get_curves(
        self,
        single_scans, single_analyzers,
        scanning_type=False,
        single_image=None,
        slices=1,
        normalize_scans_before_sum=False,
        normalize_analyzers_before_sum=False,
        poly_order=None
    ):
        """
        Specify *referenceResult* if difference should be calculated.
        """

        in_e, out_e = self.in_e, self.out_e
        i, b = self.intensities, self.background
        l = self.labels.get_labels(single_scans, single_analyzers)



        no_scans = len(i)
        no_analyzers = len(i[0])
        no_points_in_e = len(i[0][0])

        # Scanning type does not work at the moment
        # if scanning_type:
        #     ii = np.empty((no_scans, no_analyzers), dtype = list)
        #     bi = np.empty((no_scans, no_analyzers), dtype = list)
        #     ei = np.empty((no_scans, no_analyzers), dtype = list)
        #
        #     # Iterate scans
        #     z = zip(range(len(i)), i, b)
        #     for ind_s, il, bl in z:
        #         # Iterate analyzers
        #         for ind_a in range(no_analyzers):
        #             g1 = [np.sum(img) for img in il[ind_a]]
        #             g2 = [np.sum(img) for img in bl[ind_a]]
        #             ii[ind_s, ind_a] = np.array(g1)
        #             bi[ind_s, ind_a] = np.array(g2)
        #             ei[ind_s, ind_a] = np.array(in_e[ind_s])
        #
        # else:

        ii = []
        bi = []

        # Iterate scans
        z = zip(range(len(i)), i, b)
        for ind, il, bl in z:
            # if not single_image is None: # Single image does not work at the moment
            #     if slices == 1:
            #         ii.append(il[:, single_image])
            #         bi.append(bl[:, single_image])
            #     else:
            #         i0 = single_image - int(slices / 2)
            #         i1 = i0 + slices
            #         if i0 < 0:
            #             i0 = 0
            #
            #         nosey.Log.debug("Plotting slices from {} - {}".format(i0, i1))
            #         ii.append(np.sum(il[:, i0:i1], axis = 1))
            #         bi.append(np.sum(bl[:, i0:i1], axis = 1))
            # else:

            ii.append(np.sum(il, axis=1))
            bi.append(np.sum(bl, axis=1))

        ii = np.array(ii)
        bi = np.array(bi)
        ei = np.array(out_e)

        if not single_analyzers:
            ei, ii, bi = self.sum_analyzers(
                ei, ii, bi, normalize_analyzers_before_sum)

        if not single_scans:
            ei, ii, bi = self.sum_scans(ei, ii, bi, normalize_scans_before_sum)

        if poly_order is not None:
            for scan_index in range(bi.shape[0]):
                for analyzer_index in range(bi[scan_index].shape[0]):
                    curve = bi[scan_index, analyzer_index]
                    bi[scan_index, analyzer_index] = nmath.fit_curve(
                        curve, poly_order)

        return ei, ii, bi, l

    def getIAD(self, r, windowNorm=None, windowCOM=None):

        er, ir, br, _ = r.get_curves(False, False)
        e, i, b, _ = self.get_curves(False, False)
        er, ir, br = er[0, 0], ir[0, 0], br[0, 0]
        e, i, b = e[0, 0], i[0, 0], b[0, 0]
        com_shift = nmath.calculateCOM(
            er, ir - br) - nmath.calculateCOM(e, i - b)
        e += com_shift
        e, i, b = nmath.interpolate_and_sum(
            [e, er], [i, -1 * ir], [b, br], True, windowNorm)

        if windowCOM is None:
            iad = np.sum(np.abs(i))
        else:
            ind0 = np.argmin(np.abs(e - windowCOM[0]))
            ind1 = np.argmin(np.abs(e - windowCOM[1]))
            iad = np.sum(np.abs(i[ind0:ind1]))
        return iad

    def sum_analyzers(
            self,
            energies,
            intensities,
            backgrounds,
            normalize_before_sum=False):
        """
        Interpolate spectra for multiple analyzers linearly and sum them
        scan-wise.

        S               Number of scans (of 1 if summed)
        A               Number of analyzers (of 1 if summed)
        P               Number of points along energy axis

        energies        Array (S x A x P)
        intensities     Array (S x A x P)
        backgrounds     Array (S x A x P)
        """

        energies_summed = np.empty((len(energies), 1), dtype=list)
        intensities_summed = np.empty((len(energies), 1), dtype=list)
        backgrounds_summed = np.empty((len(energies), 1), dtype=list)

        # Iterate over scans
        z = zip(range(len(energies)), energies, intensities, backgrounds)
        for ind, energy, intensity, background in z:

            ce, ii, b = nmath.interpolate_and_sum(
                energy, intensity, background, normalize_before_sum)

            energies_summed[ind] = [ce]
            intensities_summed[ind] = [ii]
            backgrounds_summed[ind] = [b]

        return energies_summed, intensities_summed, backgrounds_summed

    def sum_scans(
            self,
            energies,
            intensities,
            backgrounds,
            normalize_before_sum=False):
        """
        Interpolate spectra for multiple scans linearly and sum them
        analyzer-wise.

        S               Number of scans (of 1 if summed)
        A               Number of analyzers (of 1 if summed)
        P               Number of points along energy axis

        energies        Array (S x A x P)
        intensities     Array (S x A x P)
        backgrounds     Array (S x A x P)
        """

        n_analyzers = len(energies[0])
        energies_summed = np.empty((1, n_analyzers), dtype=list)
        intensities_summed = np.empty((1, n_analyzers), dtype=list)
        backgrounds_summed = np.empty((1, n_analyzers), dtype=list)

        # Iterate over analyzers
        z = zip(range(n_analyzers), energies.T, intensities.T, backgrounds.T)
        for ind, energy, intensity, background in z:
            ce, ii, b = nmath.interpolate_and_sum(
                energy, intensity, background, normalize_before_sum)

            energies_summed.T[ind] = [ce]
            intensities_summed.T[ind] = [ii]
            backgrounds_summed.T[ind] = [b]

        return energies_summed, intensities_summed, backgrounds_summed

    # def _interpolate_and_sum(self, energy, intensity, background, normalize_before_sum = False, window = None):
    #
    #     min_energy = np.max(list(np.min(e) for e in energy))
    #     max_energy = np.min(list(np.max(e) for e in energy))
    #     # print("min_energy", min_energy, "max_energy", max_energy)
    #
    #     points = np.max(list([len(i) for i in intensity]))
    #     ii = np.zeros(points, dtype = np.float)
    #     bg = np.zeros(points, dtype = np.float)
    #     ce = np.linspace(min_energy, max_energy, points)
    #
    #     for e, i, b in zip(energy, intensity, background):
    #
    #         fi = interp.interp1d(e, i)
    #         fb = interp.interp1d(e, b)
    #         if normalize_before_sum:
    #             b           = fb(ce)
    #             i, factor   = normalize_curve(ce, fi(ce) - b, window)
    #             b          *= factor
    #         else:
    #             b           = fb(ce)
    #             i           = fi(ce)
    #         ii += i
    #         bg += b
    #
    #     return ce, ii, bg

    #
    # def _normalize(self, i, b, area = 1000):
    #     factor = 1 / np.sum(np.abs(i - b)) * area
    #     return i * factor, factor

    #
    # def _calculateCOM(self, e, i):
    #     cumsum = np.cumsum(i)
    #     f = interp.interp1d(cumsum, e)
    #     return float(f(0.5*np.max(cumsum)))
