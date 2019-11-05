""" Import module. An import policy will take a number of files and decide how
    to handle the import process:
    a) Files belong to one scan and will be returned as one set of data
       e.g. a FEL run, split over several HDF5 files
    b) Files each belong to their own scan and will be returned as multiple sets
       e.g. SPOCK/SPECK logfiles, each listing a set of subfiles (e.g. images)
"""

import os
import re
import pickle
import numpy as np
import h5py
import tifffile as tiff

import matplotlib.pyplot as plt


class ImportPolicy(object):
    """An import policy on how to extract data from a selection of files."""

    def getImages(self, files, roi=None, indizes=None):
        raise NotImplementedError()

    def getI0(self, files, indizes=None):
        raise NotImplementedError()

    def getTrainID(self, files, indizes=None):
        raise NotImplementedError()

    def getEnergy(self, files, indizes=None):
        raise NotImplementedError()


# class DELTARecipe(Recipe):
#     """DELTA: Recipe for PILATUS detector at BL8, DELTA storage ring, Dortmund."""
#
#     def getImages(self, filename, roi=None, indizes=None):
#         if roi:
#             x0, y0, x1, y1 = roi
#         else:
#             x0, y0, x1, y1 = 0, 0, 487, 195
#
#         dtype = '({},{})i4'.format(y1 - y0, x1 - x0)
#         images = np.empty(1, dtype=dtype)
#
#         images[0] = tiff.imread(filename)[y0:y1, x0:x1]
#
#         return images
#
#     def getI0(self, log_file, indizes=None, cols=14, i0_column=4):
#         with open(log_file, 'r') as content_file:
#             content = content_file.read()
#
#         pattern = r'\s*([+-]*\d+\.*\d*[e0-9-+]*)\s' * cols
#         matches = re.findall(pattern, content)
#
#         if not indizes:
#             indizes = range(len(matches))
#
#         i0 = np.empty(len(indizes))
#         for index, match in enumerate(matches):
#             if index not in indizes:
#                 continue
#
#             i0[indizes.index(index)] = match[i0_column]
#
#         return i0
#
#     def getTrainID(self, log_file, indizes=None):
#         with open(log_file, 'r') as content_file:
#             content = content_file.read()
#
#         pattern = r'\s*([+-]*\d+\.*\d*[e0-9-+]*)\s' * cols
#         matches = re.findall(pattern, content)
#
#         if not indizes:
#             indizes = range(len(matches))
#
#         return np.arange(len(indizes))
#
#     def getEnergy(self, log_file, indizes=None, cols=14, energy_column=3):
#         with open(log_file, 'r') as content_file:
#             content = content_file.read()
#
#         pattern = r'\s*([+-]*\d+\.*\d*[e0-9-+]*)\s' * cols
#         matches = re.findall(pattern, content)
#
#         if not indizes:
#             indizes = range(len(matches))
#
#         energy = np.empty(len(indizes))
#         for index, match in enumerate(matches):
#             if index not in indizes:
#                 continue
#
#             energy[indizes.index(index)] = match[energy_column]
#
#         return energy
#
#
# class XFELRecipe(Recipe):
#     pass

class PETRA(ImportPolicy):
    """PETRA: PILATUS detector at P01, PETRA III storage ring, Germany."""

    def read(self, files, roi = None, cols=14, energy_column=3, i0_column=4):
        """ Policy: *files* is expected to be a list of *.FIO log files and each
            entry will be treated as a new scan/run.
        """

        scan_data = []

        if roi:
            x0, y0, x1, y1 = roi
        else:
            x0, y0, x1, y1 = 0, 0, 487, 195

        for filename in files:

            # Parse log file
            with open(filename, 'r') as file:
                file_str = file.read()

            pattern = r'\s*([+-]*\d+\.*\d*[e0-9-+]*)\s' * cols
            matches = re.findall(pattern, file_str)

            i0, energies = np.empty(len(matches)), np.empty(len(matches))
            for idx, match in enumerate(matches):
                i0[idx] = match[i0_column]
                energies[idx] = match[energy_column]

            # Read images
            img_folder_path, _ = os.path.splitext(filename)
            img_folder_path = os.path.join(img_folder_path, 'pilatus_100k')
            img_files = sorted(os.listdir(img_folder_path))
            img_files = list([os.path.join(img_folder_path, f) for f in img_files])

            # Throw out unwanted files
            img_files = list(f for f in img_files if '.tif' in f)

            dtype = '({},{})i4'.format(y1 - y0, x1 - x0)
            images = np.empty(len(img_files), dtype=dtype)

            for idx, img_file in enumerate(img_files):
                images[idx] = tiff.imread(img_file)

            d = {
                'name' : os.path.split(os.path.splitext(filename)[0])[1],
                'images' : images,
                'i0' : i0,
                'energies' : energies
            }

            scan_data.append(d)

        return scan_data


# class SACLARecipe(Recipe):
#     pass
#
#
# class SOLEILRecipe(Recipe):
#     """SOLEIL: Recipe for PILATUS detector at GALAXIES, SOLEIL storage ring, France."""
#
#     def getImages(self, filename, roi=None, indizes=None):
#         if roi:
#             x0, y0, x1, y1 = roi
#         else:
#             x0, y0, x1, y1 = 0, 0, 487, 195
#
#         with h5py.File(filename, 'r') as file:
#             pattern = r'(.*?)\d{6}\.nxs'
#             nameOnly = os.path.split(filename)[1]
#             match = re.findall(pattern, nameOnly)[0]
#             path = '/entry/scan_data/{}image'
#             path = path.format(match)
#             images = file[path][:, y0:y1, x0:x1]
#
#         if not indizes:
#             indizes = range(images.shape[0])
#
#         dtype = '({},{})i4'.format(y1 - y0, x1 - x0)
#         images_filtered = np.empty(len(indizes), dtype=dtype)
#
#         for index, img in enumerate(images):
#             if index not in indizes:
#                 continue
#
#             images_filtered[indizes.index(index)] = img
#         return images
#
#     def getI0(self, log_file, indizes=None):
#         with h5py.File(log_file, 'r') as file:
#             i0 = file['/root_spyc_config1d_RIXS_00001/scan_data/data_03'][:]
#
#         if not indizes:
#             indizes = range(len(i0))
#
#         i0 = np.empty(len(indizes))
#         for index, value in enumerate(i0):
#             if index not in indizes:
#                 continue
#
#             i0[indizes.index(index)] = value
#
#         return i0
#
#     def getEnergy(self, log_file, indizes=None, cols=14, energy_column=3):
#         with h5py.File(log_file, 'r') as file:
#             energy = file['/root_spyc_config1d_RIXS_00001/GALAXIES/Monochromator/energy'][:]
#
#         if not indizes:
#             indizes = range(len(energy))
#
#         energy = np.empty(len(indizes))
#         for index, value in enumerate(energy):
#             if index not in indizes:
#                 continue
#
#             energy[indizes.index(index)] = value
#
#         return energy
