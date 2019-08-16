import tifffile as tiff
import h5py

import nosey

p = nosey.DELTA_ImportPolicy()

run1 = nosey.Run(name = 'Run 1')
base_name = 'data/run08_19_00112_0000{}.tif'
detector_files  = [base_name.format(i) for i in range(1, 6 + 1)]
run1.read(p, detector_files, 'data/run08_19_00112.FIO')

run2 = nosey.Run(name = 'Run 2')
base_name = 'data/run08_19_00116_0000{}.tif'
detector_files  = [base_name.format(i) for i in range(1, 6 + 1)]
run2.read(p, detector_files, 'data/run08_19_00116.FIO')
