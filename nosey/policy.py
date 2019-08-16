"""Import module."""

import os
import re
import pickle
import numpy as np

import nosey.math as nmath
import nosey

try:
    import h5py
except:
    pass

try:
    import tifffile as tiff
except:
    pass


class ImportPolicy(object):
    def __init__(self):
        super().__init__()

    def read(self, *args, **kwargs):
        fmt = "{} does not have a valid 'read()' method."
        raise NotImplementedError(fmt.format(type(self).__name__))


class DELTA_ImportPolicy(ImportPolicy):
    """DELTA: Recipe for PILATUS detector at BL8, DELTA storage ring, Dortmund."""

    def __init__(self, log_columns = 17, i0_column = 5, scan_column = 0):
        self.log_columns    = log_columns
        self.i0_column      = i0_column
        self.scan_column    = scan_column


    def read(self, files, log_file):
        x0, y0, x1, y1 = 0, 0, 487, 195
        dtype = '({},{})float64'.format(y1-y0, x1-x0)

        images = np.empty(len(files), dtype = dtype)
        for ind, filename in enumerate(files):
            images[ind] = tiff.imread(filename)[y0:y1, x0:x1]

        with open(log_file, 'r') as content_file:
            content = content_file.read()

        pattern = r'\s*([+-]*\d+\.*\d*[e0-9-+]*)\s' * self.log_columns
        matches = re.findall(pattern, content)

        i0 = np.empty(len(matches))
        steps = np.empty(len(matches))
        for index, match in enumerate(matches):
            i0[index] = match[self.i0_column]
            steps[index] = match[self.scan_column]


        steps, indizes  = nmath.getUniqueValues(steps, return_indizes = True)
        images_summed   = np.empty(len(steps), dtype = dtype)
        for step_index, image_indizes in enumerate(indizes):
            images_summed[step_index] = np.sum(images[image_indizes], axis = 0)

        return images_summed, steps, i0



class SOLEIL_ImportPolicy(ImportPolicy):
    """SOLEIL: Recipe for PILATUS detector at GALAXIES, SOLEIL storage ring, France."""

    def getImages(self, filename, roi = None, indizes = None):
        if roi:
            x0, y0, x1, y1 = roi
        else:
            x0, y0, x1, y1 = 0, 0, 487, 195

        with h5py.File(filename, 'r') as file:
            pattern = r'(.*?)\d{6}\.nxs'
            nameOnly = os.path.split(filename)[1]
            match = re.findall(pattern, nameOnly)[0]
            path = '/entry/scan_data/{}image'
            path = path.format(match)
            images = file[path][:, y0:y1, x0:x1]

        if not indizes:
            indizes = range(images.shape[0])

        dtype = '({},{})i4'.format(y1-y0, x1-x0)
        images_filtered = np.empty(len(indizes), dtype = dtype)

        for index, img in enumerate(images):
            if not index in indizes:
                continue

            images_filtered[indizes.index(index)] = img
        return images


    def getI0(self, log_file, indizes = None):
        with h5py.File(log_file, 'r') as file:
            i0 = file['/root_spyc_config1d_RIXS_00001/scan_data/data_03'][:]


        if not indizes:
            indizes = range(len(i0))

        i0 = np.empty(len(indizes))
        for index, value in enumerate(i0):
            if not index in indizes:
                continue

            i0[indizes.index(index)] = value

        return i0


    def getEnergy(self, log_file, indizes = None, cols = 14, energy_column = 3):
            with h5py.File(log_file, 'r') as file:
                energy = file['/root_spyc_config1d_RIXS_00001/GALAXIES/Monochromator/energy'][:]


            if not indizes:
                indizes = range(len(energy))

            energy = np.empty(len(indizes))
            for index, value in enumerate(energy):
                if not index in indizes:
                    continue

                energy[indizes.index(index)] = value

            return energy
