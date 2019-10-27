"""Import module."""

import os
import re
import pickle
import numpy as np
import h5py
import tifffile as tiff


class Recipe(object):
    """A recipe on how to extract data from a selection of files."""

    @classmethod
    def load(cls, filepath):
        return pickle.load(open(filepath, 'rb'))

    @classmethod
    def save(self, filepath, recipes):
        pickle.dump(recipes, open(filepath, 'wb'))

    def getImages(self, files, roi=None, indizes=None):
        raise NotImplementedError()

    def getI0(self, files, indizes=None):
        raise NotImplementedError()

    def getTrainID(self, files, indizes=None):
        raise NotImplementedError()

    def getEnergy(self, files, indizes=None):
        raise NotImplementedError()


class DELTARecipe(Recipe):
    """ DELTA: Recipe for PILATUS detector at BL8, DELTA storage ring,
        Dortmund."""

    def getImages(self, filename, roi=None, indizes=None):
        if roi:
            x0, y0, x1, y1 = roi
        else:
            x0, y0, x1, y1 = 0, 0, 487, 195

        dtype = '({},{})i4'.format(y1 - y0, x1 - x0)
        images = np.empty(1, dtype=dtype)

        images[0] = tiff.imread(filename)[y0:y1, x0:x1]

        return images

    def getI0(self, log_file, indizes=None, cols=14, i0_column=4):
        with open(log_file, 'r') as content_file:
            content = content_file.read()

        pattern = r'\s*([+-]*\d+\.*\d*[e0-9-+]*)\s' * cols
        matches = re.findall(pattern, content)

        if not indizes:
            indizes = range(len(matches))

        i0 = np.empty(len(indizes))
        for index, match in enumerate(matches):
            if index not in indizes:
                continue

            i0[indizes.index(index)] = match[i0_column]

        return i0

    def getTrainID(self, log_file, indizes=None):
        with open(log_file, 'r') as content_file:
            content = content_file.read()

        pattern = r'\s*([+-]*\d+\.*\d*[e0-9-+]*)\s' * cols
        matches = re.findall(pattern, content)

        if not indizes:
            indizes = range(len(matches))

        return np.arange(len(indizes))

    def getEnergy(self, log_file, indizes=None, cols=14, energy_column=3):
        with open(log_file, 'r') as content_file:
            content = content_file.read()

        pattern = r'\s*([+-]*\d+\.*\d*[e0-9-+]*)\s' * cols
        matches = re.findall(pattern, content)

        if not indizes:
            indizes = range(len(matches))

        energy = np.empty(len(indizes))
        for index, match in enumerate(matches):
            if index not in indizes:
                continue

            energy[indizes.index(index)] = match[energy_column]

        return energy


class XFELRecipe(Recipe):
    """ XFEL: Recipe for JUNGFRAU detector at FXE, Euroepan XFEL,
        Germany."""

    def getImages(self, filename):
        path = '/INSTRUMENT/FXE_XAD_JF1M/DET/RECEIVER-2:daqOutput/data/adc'
        with h5py.File(filename, 'r') as file:
            t = file['/INSTRUMENT/FXE_XAD_JF1M/DET/RECEIVER-2:daqOutput/data/trainId'][:]
            images = file[path][:]
            # images = images[np.where(t > 0)[0], 0, :, :]

            print(images.shape)
        return images


class PETRARecipe(Recipe):
    pass


class SACLARecipe(Recipe):
    pass


class SOLEILRecipe(Recipe):
    """ SOLEIL: Recipe for PILATUS detector at GALAXIES, SOLEIL storage ring,
        France."""

    def getImages(self, filename, roi=None, indizes=None):
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

        dtype = '({},{})i4'.format(y1 - y0, x1 - x0)
        images_filtered = np.empty(len(indizes), dtype=dtype)

        for index, img in enumerate(images):
            if index not in indizes:
                continue

            images_filtered[indizes.index(index)] = img
        return images

    def getI0(self, log_file, indizes=None):
        with h5py.File(log_file, 'r') as file:
            i0 = file['/root_spyc_config1d_RIXS_00001/scan_data/data_03'][:]

        if not indizes:
            indizes = range(len(i0))

        i0 = np.empty(len(indizes))
        for index, value in enumerate(i0):
            if index not in indizes:
                continue

            i0[indizes.index(index)] = value

        return i0

    def getEnergy(self, log_file, indizes=None, cols=14, energy_column=3):
        with h5py.File(log_file, 'r') as file:
            energy = file['/root_spyc_config1d_RIXS_00001/GALAXIES/Monochromator/energy'][:]

        if not indizes:
            indizes = range(len(energy))

        energy = np.empty(len(indizes))
        for index, value in enumerate(energy):
            if index not in indizes:
                continue

            energy[indizes.index(index)] = value

        return energy


class ALBARecipe(Recipe):
    """ ALBA: Recipe for MYTHEN detector at CLAESS BL22,
        ALBA storage ring, Spain."""

    def getImages(self, filename, roi=None, indizes=None):

        file_arr    = np.loadtxt(filename, skiprows = 5).T
        images      = np.reshape(file_arr[1], (1, 1, len(file_arr[1])))

        if roi:
            x0, y0, x1, y1 = roi
        else:
            x0, y0, x1, y1 = 0, 0, len(images[0,0]), 1


        if not indizes:
            indizes = range(images.shape[0])

        dtype = '({},{})i4'.format(y1 - y0, x1 - x0)
        images_filtered = np.empty(len(indizes), dtype=dtype)

        for index, img in enumerate(images):
            if index not in indizes:
                continue

            images_filtered[indizes.index(index)] = img
        return images
