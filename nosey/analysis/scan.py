"""This module describes a data run ("scan")."""

import os
import re
import time
import numpy as np
import nosey

class Scan(object):
    def __init__(self, log_file, image_files):
        """ Specify *logfile* as namestring and list of *image_files*.
        Assumes that logfile holds energy for each image.
        """
        self.name           = log_file
        self.log_file       = log_file
        self.files          = image_files
        self.images         = None
        self.energies       = None
        self.monitor        = None
        self.loaded         = False
        self.range          = [0, len(image_files)]


    @property
    def images(self):
        return self.__images[slice(*self.range)]


    @property
    def energies(self):
        return self.__energies[slice(*self.range)]


    @property
    def monitor(self):
        return self.__monitor[slice(*self.range)]


    @images.setter
    def images(self, images):
        self.__images = images


    @energies.setter
    def energies(self, energies):
        self.__energies = energies


    @monitor.setter
    def monitor(self, monitor):
        self.__monitor = monitor


    def read_logfile(self, recipe):

        self.energies   = recipe.getEnergy(self.log_file)
        self.monitor    = recipe.getI0(self.log_file)

        # plt.plot(pin2)
        # plt.show()


    def read_files(self, recipe, callback = None):

        self.images = recipe.getImages(self.files)
        self.loaded = True

        img_shape           = self.images.shape
        shape               = (nosey.MAX_NUMBER_ANALYZERS, img_shape[0], img_shape[2])
        self.out_e           = np.empty((nosey.MAX_NUMBER_ANALYZERS, img_shape[2]))
        self.intensity       = np.empty(shape)
        self.background      = np.empty(shape)
        self.in_e            = np.arange(self.images.shape[0])
        self.fits            = np.empty(shape)

        # arr = np.array(self.images)
        # arr = np.sum(arr, axis = 0)
        # plt.imshow(np.log(arr))
        # plt.show()


    def get_energy_spectrum(self, analyzers):
        s = np.s_[0:len(analyzers)]

        for ind, an in enumerate(analyzers):
            ei, ii, bg, fit = an.counts(self.images)
            self.out_e[ind] = ei
            self.intensity[ind] = ii
            self.background[ind] = bg
            self.fits[ind] = fit

            # I0
            # intensity[ind] /= self.monitor
            # background[ind] /= self.monitor

        return self.in_e, self.out_e[s], self.intensity[s], self.background[s], self.fits[s]

        # for ind, an in enumerate(analyzers):
        #     b, s = an.get_signal_series(images=self.images)
        #
        #     for ind in range(len(s)):
        #         s[ind] /= self.monitor[ind]
        #
        #     bg = np.zeros(s.shape)
        #     out_e.append(b)
        #     intensity.append(s)
        #     background.append(bg)
        #
        # return in_e, out_e, intensity, background

    #
    # def set_background_model(self, bg_model):
    #     self.bg_model = bg_model
