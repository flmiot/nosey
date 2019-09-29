"""Analysis result"""

import numpy as np
import scipy.interpolate as interp

import nosey
from nosey.label import Label
import nosey.math as nmath

import matplotlib.pyplot as plt

class Analysis(object):
    def __init__(self):

        self.results        = {'completed':False, 'steps_summed':True}
        self.labels         = Label()


    def get_spectrum(self, runs, analyzers, out = None, **opts):
        pass


    def run(self, runs, analyzers, sum_steps = True, out = None):
        """ Run the analysis.

        Args:
            runs        (list)
                        list of Run objects

            analyzers   (list)
                        list of Analyzer objects

            sum_steps   (bool) [default: True]
                        Sum the images of each run before integration

            out     (dict) [default: None]
                    dict of (preallocated) memory. If None new arrays will be
                    allocated and returned. If specified content has to be:

                    "ea":       nd.array ()
                    "ii":       nd.array ()
                    "er_ii":    nd.array ()
                    "ii_bg":    nd.array ()
                    "er_ii_bg": nd.array ()
                    "fit":      nd.array ()
                    "stop":     nd.array ()

        Raises:
            None

        Returns:
            None
        """

        if len(runs) < 1:
            raise ValueError("No active runs!")
        if len(analyzers) < 1:
            raise ValueError("No active analyzers!")

        self.results['completed']       = False
        self.results['analyzers']       = analyzers
        self.results['runs']            = runs
        self.results['steps_summed']    = sum_steps

        if sum_steps:
            if out is None:
                shape = (len(runs) * 1, len(analyzers), runs[0].size()[2])
                self.results['ea']          = np.empty(shape)
                self.results['ii']          = np.empty(shape)
                self.results['er_ii']       = np.empty(shape)
                self.results['ii_bg']       = np.empty(shape)
                self.results['er_ii_bg']    = np.empty(shape)
                self.results['fit']         = np.empty(shape)

                sh = (len(runs) * 1, len(analyzers))
                self.results['stop']        = np.empty(sh)

            else:
                self.results['ea']          = out['ea']
                self.results['ii']          = out['ii']
                self.results['er_ii']       = out['er_ii']
                self.results['ii_bg']       = out['ii_bg']
                self.results['er_ii_bg']    = out['er_ii_bg']
                self.results['fit']         = out['fit']
                self.results['stop']        = out['stop']

            for i, run in enumerate(runs):
                out = {
                    'ea' :      self.results['ea'][i:i+1],
                    'ii' :      self.results['ii'][i:i+1],
                    'er_ii':    self.results['er_ii'][i:i+1],
                    'ii_bg':    self.results['ii_bg'][i:i+1],
                    'er_ii_bg': self.results['er_ii_bg'][i:i+1],
                    'fit':      self.results['fit'][i:i+1],
                    'stop':     self.results['stop'][i:i+1],
                    }

                run.get_spectrum(analyzers, sum_steps = True, out = out)
                d = {run.name : list([a.name for a in analyzers])}
                self.labels.add_scan_labels(d)

        else:
            steps = 0
            for scan in self.scans:
                steps += len(scan.steps)
            shape = (steps, len(analyzers), runs[0].size()[2])

        self.results['completed'] = True


    def get_curves(self,
        single_scans,
        single_analyzers,
        sum_steps = True,
        single_image = None,
        slices = 1,
        poly_order = None):

        if not self.results['completed']:
            raise RuntimeError(
            "Analysis result is none. "
            "'run()' method needs to be called first.")

        if self.results['steps_summed'] != sum_steps:
            self.run(
                self.results['runs'], self.results['analyzers'],
                sum_steps = sum_steps)
            fmt = "Analysis 'run()' method was called with sum_steps{}, because"
            "it was previously run with sum_steps={}."
            nosey.Log.warning(fmt.format(sum_steps, not sum_steps))


        # in_e, out_e = self.results['ea'], self.results['ea']
        # i, b = self.results['ii'], self.results['ii_bg']
        l = self.labels.get_labels(single_scans, single_analyzers)
        #
        # shape = ()
        # scans = 1
        #
        # no_analyzers = len(i[0])
        # no_points_in_e = len(i[0][0])

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
        #
        # ii = []
        # bi = []
        #
        # # Iterate scans
        # z = zip(range(len(i)), i, b)
        # for ind, il, bl in z:
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
        #
        #     ii.append(np.sum(il, axis = 1))
        #     bi.append(np.sum(bl, axis = 1))
        #
        # ii = np.array(ii)
        # bi = np.array(bi)
        # ei = np.array(out_e)
        #
        # print(self.results['ii_bg'].shape)

        ei, ii, bi = self.results['ea'], self.results['ii'], self.results['ii_bg']

        if not single_analyzers:
            ei, ii, bi = self.sum_analyzers(ei, ii, bi)

        if not single_scans:
            ei, ii, bi = self.sum_scans(ei, ii, bi)

        if poly_order is not None:
            for scan_index in range(bi.shape[0]):
                for analyzer_index in range(bi[scan_index].shape[0]):
                    curve = bi[scan_index, analyzer_index]
                    bi[scan_index, analyzer_index] = nmath.fit_curve(curve, poly_order)

        return ei, ii, bi, l


    def sum_analyzers(self, energies, intensities, backgrounds):
        """
        Interpolate spectra for multiple analyzers linearly and sum them
        scan-wise.

        S               Number of scans (of 1 if summed)
        A               Number of analyzers (of 1 if summed)
        P               Number of points along energy axis

        energies        Array (S x A x P)
        intensities     Array (S x A x P)
        backgrounds     Array (S x A x P)

        List of A x P arrays
        """

        S = len(intensities)
        A = 1
        N = 1
        P = intensities[0].shape[1]

        energies_summed     = np.empty( (S, A, P) )
        intensities_summed  = np.empty( (S, A, P) )
        backgrounds_summed  = np.empty( (S, A, P) )

        # # Iterate over scans
        z = zip(range(len(energies)), energies, intensities, backgrounds)
        for ind, energy, intensity, background in z:

            ce, ii, b = nmath.interpolate_and_sum(energy, intensity, background)

            energies_summed[ind]    = ce
            intensities_summed[ind] = ii
            backgrounds_summed[ind] = b

        return energies_summed, intensities_summed, backgrounds_summed


    def sum_scans(self, energies, intensities, backgrounds):
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

        S = 1
        A = intensities[0].shape[0]
        N = 1
        P = intensities[0].shape[1]



        energies_summed = np.empty( (S, A, P) )
        intensities_summed = np.empty( (S, A, P) )
        backgrounds_summed = np.empty( (S, A, P) )

        # Iterate over analyzers


        l = [np.transpose(a, (1,0,2)) for a in [energies, intensities, backgrounds]]
        z = zip(range(A), *l)
        for ind, energy, intensity, background in z:

            ce, ii, b = nmath.interpolate_and_sum(energy, intensity, background)

            np.transpose(energies_summed, (1,0,2))[ind]      = ce
            np.transpose(intensities_summed, (1,0,2))[ind]   = ii
            np.transpose(backgrounds_summed, (1,0,2))[ind]   = b

        return energies_summed, intensities_summed, backgrounds_summed

class AnalysisError(Exception):

    pass

# def getIAD(self, r, windowNorm = None, windowCOM = None):
#
#     er, ir, br, _       = r.get_curves(False, False)
#     e, i, b, _          = self.get_curves(False, False)
#     er, ir, br          = er[0,0], ir[0,0], br[0,0]
#     e, i, b             = e[0,0], i[0,0], b[0,0]
#     com_shift           = nmath.calculateCOM(er, ir-br) - nmath.calculateCOM(e, i-b)
#     e                  += com_shift
#     e, i, b             = nmath.interpolate_and_sum([e, er], [i, -1 * ir], [b, br], True, windowNorm)
#
#     if windowCOM is None:
#         iad             = np.sum(np.abs(i))
#     else:
#         ind0            = np.argmin(np.abs(e - windowCOM[0]))
#         ind1            = np.argmin(np.abs(e - windowCOM[1]))
#         iad             = np.sum(np.abs(i[ind0:ind1]))
#     return iad
#


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
