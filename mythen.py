import os
import re
import numpy as np
import scipy.interpolate as interp
import matplotlib.pyplot as plt
import json

folder = 'C:/Users/otteflor/Google Drive/Data - ALBA beamtime Oct 2019/rixs/'

def read_energy_calibration(filename):
    with open(filename, 'r') as file:
        file_str = file.read()
        d = json.loads(file_str)
    return d

# def read(filename):
#     pattern = r'@A (.*)\n(.*)'
#
#     with open(filename, 'r') as file:
#         file_str = file.read()
#
#     counts, counters    = np.array(re.findall(pattern, file_str)).T
#     counts_arr          = np.empty((len(counts), 1280))
#     counters_arr        = np.empty((len(counts), 25))
#
#     for ind, mythen_counts, count in zip(range(len(counts)), counts, counters):
#         str_counts          = re.findall(r'(\d+)', mythen_counts)
#         str_counters        = re.findall(r'(\d+\.*\d*)', count)
#         counts_arr[ind]     = [float(f) for f in str_counts]
#         counters_arr[ind]   = [float(f) for f in str_counters]
#
#     return counts_arr, counters_arr.T

def read(filename):
    return np.loadtxt(filename, skiprows = 1)


def sumSpectra(spectra, shifts):
    points = len(spectra[0])
    summed = np.zeros(points)
    shifted = []
    x0 = np.max([0, np.max(shifts)])
    x1 = np.min([points, points + np.min(shifts)])
    new_x = np.linspace(x0, x1, points)
    # print(new_x)
    for ind, shift, s in zip(range(len(shifts)), shifts, spectra):

        x = np.linspace(0, len(s), len(s))
        f = interp.interp1d(x, s)
        summed += f(new_x - shift)
        shifted.append([new_x, f(new_x - shift)])


    return summed, shifted

def shiftRIXS(spectra, shifts):
    shifted = []
    for ind, shift, s in zip(range(len(shifts)), shifts, spectra):
        shifted_image = np.empty(s.shape)
        for ind, pixelRow in enumerate(s):
            x = np.arange(len(pixelRow))
            f = interp.interp1d(x, pixelRow, bounds_error = False, fill_value = 0)
            shifted_image[ind] = f(x + shift)
        shifted.append(shifted_image)

    return shifted


files_all = [os.path.join(folder, f) for f in sorted(os.listdir(folder))]
files_all = [f for f in files_all if '_mythen_data' in f]

files_co3 = [f for f in files_all if 'co3' in f]

files = [f for f in files_co3 if 'ec7635' in f]
sh = (len(files), ) + read(files[0]).shape
counts_7635 = np.empty(sh)
for ind, file in enumerate(files):
    counts_7635[ind]= read(file)


files = [f for f in files_co3 if 'ec7645' in f]
sh = (len(files), ) + read(files[0]).shape
counts_7645 = np.empty(sh)
for ind, file in enumerate(files):
    counts_7645[ind]= read(file)
myMax = 3000

files = [f for f in files_co3 if 'ec7655' in f]
sh = (len(files), ) + read(files[0]).shape
counts_7655 = np.empty(sh)
for ind, file in enumerate(files):
    counts_7655[ind]= read(file)

# plt.figure()
# plt.imshow(np.sum(counts_7635, axis = 0), vmin = 0, vmax = myMax)
# plt.xlim([300, 500])
# plt.title('E_c = 7635')
#
# plt.figure()
# plt.imshow(np.sum(counts_7645, axis = 0), vmin = 0, vmax = myMax)
# plt.xlim([300, 500])
# plt.title('E_c = 7645')
#
#
# plt.figure()
# plt.imshow(np.sum(counts_7655, axis = 0), vmin = 0, vmax = myMax)
# plt.xlim([300, 500])
# plt.title('E_c = 7655')

plt.figure()
for c in counts_7635[:,-1]:
    plt.plot(c)
plt.xlim([300, 500])
for c in counts_7645[:,-1]:
    plt.plot(c)
plt.xlim([300, 500])
for c in counts_7655[:,-1]:
    plt.plot(c)
plt.xlim([300, 500])

srixs = shiftRIXS([np.sum(counts_7635, axis = 0), np.sum(counts_7645, axis = 0), np.sum(counts_7635, axis = 0)], [-10/0.2, 0, -10/0.2])
sumrixs = np.sum(np.array(srixs), axis = 0)
plt.figure()
plt.imshow(np.log(sumrixs+0.001), vmin = 0, aspect = 'auto')


counts_7635_summed = np.sum(counts_7635[:,-1], axis = 0)
counts_7645_summed = np.sum(counts_7645[:,-1], axis = 0)
counts_7655_summed = np.sum(counts_7655[:,-1], axis = 0)

summed, shifted = sumSpectra([counts_7635_summed, counts_7645_summed, counts_7655_summed], [10/0.2, 0, -10/0.2])

plt.figure()
for p, label in zip(shifted, ['ec = 7635', 'ec = 7645', 'ec = 7655']):
    plt.plot(*p, label = label)
plt.plot(summed)
plt.legend()
plt.xlim([250, 550])

plt.figure()
data = np.sum(np.sum(counts_7645, axis = 0)[:, 378-10:378+10], axis = 1)
np.savetxt('co3.dat', np.array([np.arange(len(data)), data]).T)
plt.plot(data)


files_co2 = [f for f in files_all if 'Co2' in f]

files = [f for f in files_co2 if 'Ec_7635' in f]
sh = (len(files), ) + read(files[0]).shape
counts_7635 = np.empty(sh)
for ind, file in enumerate(files):
    counts_7635[ind]= read(file)


files = [f for f in files_co2 if 'Ec_7645' in f]
sh = (len(files), ) + read(files[0]).shape
counts_7645 = np.empty(sh)
for ind, file in enumerate(files):
    counts_7645[ind]= read(file)
myMax = 3000

files = [f for f in files_co2 if 'Ec_7655' in f]
sh = (len(files), ) + read(files[0]).shape
counts_7655 = np.empty(sh)
for ind, file in enumerate(files):
    counts_7655[ind]= read(file)

# plt.figure()
# plt.imshow(np.sum(counts_7635, axis = 0), vmin = 0, vmax = myMax)
# plt.xlim([300, 500])
# plt.title('E_c = 7635')
#
# plt.figure()
# plt.imshow(np.sum(counts_7645, axis = 0), vmin = 0, vmax = myMax)
# plt.xlim([300, 500])
# plt.title('E_c = 7645')
#
#
# plt.figure()
# plt.imshow(np.sum(counts_7655, axis = 0), vmin = 0, vmax = myMax)
# plt.xlim([300, 500])
# plt.title('E_c = 7655')

plt.figure()
for c in counts_7635[:,-1]:
    plt.plot(c)
plt.xlim([300, 500])
for c in counts_7645[:,-1]:
    plt.plot(c)
plt.xlim([300, 500])
for c in counts_7655[:,-1]:
    plt.plot(c)
plt.xlim([300, 500])

counts_7635_summed = np.sum(counts_7635[:,-1], axis = 0)
counts_7645_summed = np.sum(counts_7645[:,-1], axis = 0)
counts_7655_summed = np.sum(counts_7655[:,-1], axis = 0)

summed, shifted = sumSpectra([counts_7635_summed, counts_7645_summed, counts_7655_summed], [10/0.199, 0, -10/0.199])
srixs = shiftRIXS([np.sum(counts_7635, axis = 0), np.sum(counts_7645, axis = 0), np.sum(counts_7635, axis = 0)],  [-10/0.2, 0, -10/0.2])
sumrixs = np.sum(np.array(srixs), axis = 0)
plt.figure()
plt.imshow(np.log(sumrixs+0.001), vmin = 0, aspect = 'auto')

plt.figure()
for p, label in zip(shifted, ['ec = 7635', 'ec = 7645', 'ec = 7655']):
    plt.plot(*p, label = label)
plt.plot(summed)
plt.legend()
plt.xlim([250, 550])

plt.figure()
data = np.sum(np.sum(counts_7645, axis = 0)[:, 378-10:378+10], axis = 1)
np.savetxt('co2.dat', np.array([np.arange(len(data)), data]).T)
plt.plot(data)
plt.show()
