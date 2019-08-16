""" Import your own detector data with custom import policies for NOSEY.

    Custom policies should derive from nosey.ImportPolicy. To be a valid
    ImportPolicy, derived classes need to implement just one method:

    def read(self, *args, **kwargs):
        ...

    The 'read(...)' method will be called from other parts of the code. There
    is a convention that this method should return a tuple of three nd.arrays

    nd.array() with shape (N, x, y) (= images),
    nd.array() with shape (N)       (= scan steps, e.g. energy, motor position)
    nd.array() with shape (N)       (= i0, i.e. intensity normalization signal)

    where
        N Number of images
        x Detector image pixels along primary (dispersive) direction
        y Detector image pixels along secondary (non-dispersive) direction.
 """

import h5py
import nosey


# Example for a custom HDF5 import policy
class CustomPolicy(nosey.ImportPolicy):
    def __init__(self, data_path, step_path, i0_path):
        """ A custom HDF5 import policy. The arguments *data_path*, *step_path*,
            and *i0_path* are component paths inside the HDF5 file.
        """
        self.data_path  = data_path
        self.step_path  = step_path
        self.i0_path    = i0_path#
        super().__init__()


    def read(self, filenames):
        images  = []
        steps   = []
        i0      = []

        for filename in filenames:
            with h5py.File(filename, 'r') as handle:
                images.append(handle[self.data_path][:])

        return np.array(images), np.array(steps), np.array(i0)

# We use the custom policy to populate a run with data from HDF5 files
p = CustomPolicy("", "", "")
