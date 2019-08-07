import numpy as np

class DataArray(object):
    def __init__(self, images, analyzer, pixels):
        self.data           = np.empty((images, analyzer, pixels))
        self.stop           = np.empty((images, analyzer), dtype = np.uint8)


    def __setitem__(self, key, value):

        if isinstance(key, slice):
            self.data[key] = value

        elif isinstance(key, tuple):
            if len(key) < 2:
                raise IndexError("Out of dimension")

            elif len(key) == 2:
                len(value)

                images      = key[0]
                analyzers   = key[1]
                start, stop, _ = key[2].indices(self.data.shape[2])
                self.start[images, analyzers] = start
                self.stop[images, analyzers] = stop

            else:
                self.data[key] = value
        else:
            raise IndexError("Invalid slice submitted to DataArray object.")

    def __getitem__(self, key):

        if isinstance(key, slice):
            return self.data[key]
        elif isinstance(key, tuple):
            return self.data[key]
        else:
            raise IndexError("Invalid slice submitted to DataArray object.")
