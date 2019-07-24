import os
import re
import time
import numpy as np
import logging
import matplotlib.pyplot as plt # For debugging
import nosey

Log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class Scan(object):
    def __init__(self, log_file, image_files):
        """ Specify *logfile* as namestring and list of *image_files*.
        Assumes that logfile holds energy for each image.
        """
        self.name           = os.path.splitext(os.path.split(log_file)[1])[0]
        self.log_file       = log_file
        self.files          = image_files
        self.images         = None
        self.energies       = None
        self.monitor        = None
        self.active         = True
        # self.bg_model     = None
        self.calibration    = None
        self.loaded         = False
        self.offset         = [0,0]
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

        # arr = np.array(self.images)
        # arr = np.sum(arr, axis = 0)
        # plt.imshow(np.log(arr))
        # plt.show()


    def save_scan(self, path, analyzers):
        """Save energy loss spectra of this scan object into a textfile."""
        arr = np.array(self.get_energy_loss_spectrum(analyzers))
        arr = np.reshape(arr, (2*len(analyzers),-1))

        header = ''
        for ind in range(len(analyzers)):
            header += 'ene_{0} ana_{0} '.format(ind)
        np.savetxt(path, arr.T, header = header, comments = '')


    def toggle(self):
        self.active = not self.active


    def center_analyzers(self, analyzers):
        for an in analyzers:
            pixel_wise = an.pixel_wise
            an.determine_central_energy(images=self.images, base=self.energies,
                pixel_wise = pixel_wise)


    def get_energy_spectrum(self, analyzers, background_rois):

        in_e = np.arange(self.images.shape[0])
        out_e = np.empty((len(analyzers)), dtype = list)
        intensity = np.empty((len(analyzers), len(in_e)), dtype = list)
        background = np.empty((len(analyzers), len(in_e)), dtype = list)
        fits = np.empty((len(analyzers)), dtype = list)

        for ind, an in enumerate(analyzers):
            b, s, bg, fit = an.get_signal_series(images = self.images,
                background_rois = background_rois,
                calibration = self.calibration)


            print(s)
            out_e[ind] = b
            intensity[ind] = s
            background[ind] = bg
            fits[ind] = fit

            # I0
            # intensity[ind] /= self.monitor
            # background[ind] /= self.monitor

        return in_e, out_e, intensity, background, fits

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
