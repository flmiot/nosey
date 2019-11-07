import re
import numpy as np
import scipy.interpolate as interp
import matplotlib.pyplot as plt

################################################################################
# Get elastic scan peak pixel positons and write to file


class Scan(object):
    def load(self, scanID, parsed_scans):
        for id, command, match in parsed_scans:

            if id != scanID:
                continue

            print(id)

            pattern = 6 * r'(.*) ' + r'(.*)\n'
            c = re.findall(pattern , command)[0]
            res = 0.1666666666666666666666666667
            m = re.findall(r'@A(.*)\n(.*)', match)


            images = np.empty((len(m), 1140))
            i0 = np.empty(len(m))
            i1 = np.empty(len(m))
            for ind, match in zip(range(len(m)), m):
                images[ind] = list(float(f) for f in re.findall(r'\d+\.*\d*', match[0]))[0:1140]
                counters = [float(f) for f in re.findall(r'\d+\.?\d*', match[1])]
                i0[ind] = counters[4]
                i1[ind] = counters[6]
                images[ind] = images[ind] / i0[ind]

            # images = images / np.sum(images)
            # for img in images:
            #     plt.plot(img)

            # plt.show()
            #
            # plt.figure()
            # plt.plot(i1 / i0)
            # plt.show()


            self.scan = {
                'name' : scanID,
                'mythenRaw': images,
                'a_i0_1': i0,
                'a_i1_1': i1,
                'scanningRange': float(c[3]) - float(c[2]),
                'scanningStepSize': 0.1666666666666666666666666667,
                'scanningSteps' : (float(c[3]) - float(c[2]))/res,
                'scanningStart' : float(c[2]),
                'scanningEnd' :  float(c[3]),
                'integrationTime' : float(c[5])
                }

            return
        else:
            raise Exception()

    def getSpectrum(self, calibration, roi, factor):
        eV_per_pixel = (calibration(382) - calibration(381)) * factor
        scanning_x = np.linspace(self.scan['scanningStart'],
            self.scan['scanningEnd'], self.scan['scanningSteps'])
        shiftedMythenData = np.empty(self.scan['mythenRaw'].T.shape)
        for ind, pixel_row in enumerate(self.scan['mythenRaw'].T):
            shift = (-400 + ind) * eV_per_pixel
            p = interp.interp1d(scanning_x, pixel_row, fill_value = 0, bounds_error = False)
            shiftedMythenData[ind] = p(scanning_x - shift)

        # plt.figure()
        # plt.imshow(np.log(self.scan['mythenRaw']+0.001), vmin = -0.1, aspect = 'auto')
        # plt.axvline(x=400)
        # plt.figure()
        # plt.imshow(np.log(shiftedMythenData.T+0.001), vmin = -0.1, aspect = 'auto')
        # plt.axvline(x=400)
        # plt.show()
        return scanning_x, np.sum(shiftedMythenData[roi[0]:roi[1]], axis = 0)


################################################################################
# def calculateCOM(e, i, window=None):
#
#     if window is not None:
#         e0, e1 = window
#         i0, i1 = np.argmin(np.abs(e - e0)), np.argmin(np.abs(e - e1))
#         i, e = i[i0:i1], e[i0:i1]
#
#     cumsum = np.cumsum(i)
#     f = interp.interp1d(cumsum, e)
#     return float(f(0.5 * np.max(cumsum)))
#
# monos = [7630, 7635, 7640, 7640, 7645, 7650, 7650, 7655, 7660]
# ecs = [7635, 7635,7635, 7645, 7645, 7645,7655, 7655, 7655]
# scans = ['353332', '353333', '353334', '353335', '353336', '353337', '353338', '353339', '353340']
# labels = ['e_mono = {} ec = {}'.format(mono, ec) for mono, ec in zip(monos, ecs)]
#
# peak_positions = np.empty((9, 3))
#
# for ind, mono, ec, scan, label in zip(range(9), monos, ecs, scans, labels):
#     print(scan)
#     s = getScan(scan)
#     curve = np.sum(s['mythenRaw'], axis = 0)[0:1140]
#     com = calculateCOM(range(0, len(curve)), curve)
#     peak_positions[ind, 0] = mono
#     peak_positions[ind, 1] = ec
#     peak_positions[ind, 2] = com
#     plt.plot(curve, label = label)
# plt.xlim([200, 800])
# plt.legend()
# m = np.max(curve[0:1140])
# plt.ylim([0, m + 0.25*m])
# np.savetxt("calibration.txt", peak_positions, header = "mono ec pixel")
# plt.show()

################################################################################
filename = 'C:/Users/otteflor/Google Drive/Data - ALBA beamtime Oct 2019/data/20191019_00.dat'
c = np.loadtxt('calibration.txt', skiprows = 1)[3:3+3].T

def fit_curve(x, y, order=3):
    p = np.polyfit(x, y, order)
    poly = np.poly1d(p)
    return poly

x = c[0] - c[1]
y = c[2]
f = fit_curve(y, x, 2)
# plt.plot(y, x)
# plt.plot(f(x), x)
# plt.plot(f(np.linspace(-60, 60)), np.linspace(-60, 60), )
# plt.show()

################################################################################
# Load a XES scan


with open(filename, 'r') as file:
    fileString = file.read()

pattern = r'#S (\d+) (.*?\n)(.*?)\n\n'
matches = re.findall(pattern, fileString, flags = re.DOTALL)

def normalize_curve(e, i, window=None):
    """Return normalized curve and factor by which curve was scaled."""
    if window is not None:
        w0 = window[0]
        w1 = window[1]
        ind0 = np.argmin(np.abs(e - w0))
        ind1 = np.argmin(np.abs(e - w1))
    else:
        ind0 = 0
        ind1 = len(i)

    if ind1 - ind0 < 1 or min(ind0, ind1) < 0:
        raise Exception("Invalid normalization window")

    weight = np.sum(i[ind0:ind1])
    factor = np.abs(1 / weight) * 1000.
    return i * factor, factor

def analyze(scans, length, roi, output_filename, matches, calibration,
    scaling_factor = None, trim_range = None, bin = 1, background_level = None,
    background_window = None):
    s = Scan()
    spectra = np.empty((len(scans), length))
    for ind, n in enumerate(scans):
        s.load(n, matches)
        ax, spec = s.getSpectrum(calibration = calibration, roi = roi, factor = 0.995)
        spectra[ind] = spec
        plt.plot(ax, spec)

    spectra = np.mean(spectra, axis = 0)
    if scaling_factor is None:
        spectra, scaling_factor = normalize_curve(ax, spectra, window = [7621, 7660])
    else:
        spectra *= scaling_factor

    if trim is not None:
        ax, spectra = trim(ax, spectra, trim_range)

    if bin != 1:
        ax, spectra = binData(ax, spectra, bin)

    if background_level is None:
        if  background_window is not None:
            w0 = background_window[0]
            w1 = background_window[1]
            ind0 = np.argmin(np.abs(ax - w0))
            ind1 = np.argmin(np.abs(ax - w1))
            print("Background level:", np.mean(spectra[ind0:ind1]))
    else:
        spectra += background_level


    np.savetxt(output_filename, np.array([ax, spectra]).T)




    plt.figure()
    plt.plot(ax, spectra)



    return scaling_factor

def trim(x, y, range):
    w0 = range[0]
    w1 = range[1]
    ind0 = np.argmin(np.abs(x - w0))
    ind1 = np.argmin(np.abs(x - w1))
    return x[ind0:ind1], y[ind0:ind1]

def binData(x, y, bin_number = 2):
    values = np.arange(len(x))[::bin_number]
    binned_x  = np.array([x[i:i+bin_number].mean() for i in values])
    binned_y  = np.array([y[i:i+bin_number].mean() for i in values])
    return binned_x, binned_y


roi = [400-10, 400 + 10]

# BPY
# no = list(['{:.0f}'.format(f) for f in np.arange(353421, 353426)])
# sf = analyze(no, 360, roi, '80k_cobpysq2_mainline.dat', matches, f, trim_range = [7620, 7676], bin = 1, background_window = [7621, 7628])
# no = list(['{:.0f}'.format(f) for f in np.arange(353426, 353441)])
# no.remove('353430')
# no.remove('353431')
# analyze(no, 312, roi, '80k_cobpysq2_vtc.dat', matches, f, sf, trim_range = [7676, 9000], bin = 1)
# no = list(['{:.0f}'.format(f) for f in np.arange(353524, 353540)])
# # no.remove('353430')
# sf = analyze(no, 360, roi, '350k_cobpysq2_mainline.dat', matches, f, trim_range = [7620, 7676], bin = 1, background_level = -0.09780521)
# no = list(['{:.0f}'.format(f) for f in np.arange(353564, 353595)])
# # no.remove('353430')
# analyze(no, 312, roi, '350k_cobpysq2_vtc.dat', matches, f, sf, trim_range = [7676, 9000], bin = 1, background_level = -0.09780521)

# TMEDA
no = list(['{:.0f}'.format(f) for f in np.arange(353696, 353701)])
sf = analyze(no, 360, roi, '80k_cotmedasq2_mainline.dat', matches, f, trim_range = [7620, 7676], bin = 1, background_window = [7621, 7628])
no = list(['{:.0f}'.format(f) for f in np.arange(353701, 353719)])
# no.remove('353430')
# no.remove('353431')
analyze(no, 312, roi, '80k_cotmedasq2_vtc.dat', matches, f, sf, trim_range = [7676, 9000], bin = 1)
no = list(['{:.0f}'.format(f) for f in np.arange(353781, 353789)])
# no.remove('353430')
sf = analyze(no, 360, roi, '300k_cotmedasq2_mainline.dat', matches, f, trim_range = [7620, 7676], bin = 1 )
no = list(['{:.0f}'.format(f) for f in np.arange(353789, 353820)])
# no.remove('353430')
analyze(no, 312, roi, '300k_cotmedasq2_vtc.dat', matches, f, sf, trim_range = [7676, 9000], bin = 1)
