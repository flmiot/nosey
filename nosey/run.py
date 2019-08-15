"""This module describes a data run ("scan")."""

import os
import re
import time
import numpy as np
import nosey

class Run(object):
    def __init__(self, name):
        """
        """
        self.name           = name
        self.images         = None
        self.steps          = None
        self.i0             = None


    @property
    def images(self):
        return self.__images


    @images.setter
    def images(self, images):
        self.__images = images


    def __repr__(self):
        return "Run '{}' Shape: {}".format(self.name, self.size(False))


    def size(self, sum_steps = True):
        if sum_steps:
            return (1,) + self.images.shape[1:]
        else:
            return self.images.shape


    def read(self, policy, *args, **kwargs):
        self.images, self.steps, self.i0 = policy.read(*args, **kwargs)


    def get_spectrum(self, analyzers, sum_steps = True, out = None):

        if out is None:
            img_shape       = self.images.shape
            if sum_steps:
                shape       = (len(analyzers), 1, img_shape[2])
            else:
                shape       = (len(analyzers), img_shape[0], img_shape[2])
            out_e           = np.empty((len(analyzers), img_shape[2]))
            intensity       = np.empty(shape)
            errors          = np.empty(shape)
            background      = np.empty(shape)
            errors_bg       = np.empty(shape)
            in_e            = np.arange(self.images.shape[0])
            fits            = np.empty(shape)

        if sum_steps:
            new_shape = (1,) + self.images.shape[1:]
            summed = np.sum(self.images, axis = 0).reshape(new_shape)
            for ind, an in enumerate(analyzers):
                stop = an.get_roi(r_type = 'signal')[2]

                if out is None:
                    ei, ii, er, bg, er_bg, fit  = an.counts(summed)
                    out_e[ind, 0:stop]        = ei
                    intensity[ind, 0:stop]    = ii
                    errors[ind, 0:stop]       = er
                    errors_bg[ind, 0:stop]    = er_bg
                    background[ind, 0:stop]   = bg

                else:
                    out['stop'][:,ind] = stop
                    o = {
                        'ea'        : out['ea'][:, ind],
                        'ii'        : out['ii'][:, ind],
                        'ii_bg'     : out['ii_bg'][:, ind],
                        'er_ii'     : out['er_ii'][:, ind],
                        'er_ii_bg'  : out['er_ii_bg'][:, ind],
                        'fit'       : out['fit'][:, ind],
                        'stop'      : out['stop'][:, ind]
                        }

                    an.counts(summed, out = o)

        else:
            for ind, an in enumerate(analyzers):
                ei, ii, er, bg, er_bg, fit = an.counts(self.images)

                stop                        = ii.shape[1]
                out_e[ind]                  = -1
                intensity[ind]              = -1
                background[ind]             = -1
                fits[ind]                   = -1
                out_e[ind, :stop]           = ei
                intensity[ind, :, :stop]    = ii
                background[ind, :, :stop]   = bg


            # fits[ind, 0:len(fit)] = fit

            # I0
            # intensity[ind] /= self.monitor
            # background[ind] /= self.monitor

        if out is None:
            return in_e, out_e, intensity, errors, background, errors_bg, fits
