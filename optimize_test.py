import numpy as np
import timeit
import re
import array
from multiprocessing import Pool

N   = 4096
S   = 32
A   = 4
D1  = 487
D2  = 197

# Small memory chunks
# As few write/read operations as possible
#
images = np.empty((N, D2, D1), dtype = np.uint32)
spectra = np.empty((N, A, D1), dtype = np.uint32)


class A:
    def __init__(self, view_images, view_spectra):
        self.view_images = np.transpose(view_images, (1, 0, 2))
        self.view_spectra = np.transpose(view_spectra, (1, 0, 2))


    def get_spectrum(self, analyzer):
        analyzer.integrate(self.view_images, self.view_spectra)


class B:
    def __init__(self, N, D1, D2, view_spectra):
        self.images = np.empty((D2, N, D1))


    def get_spectrum(self, analyzers):
        sh      = self.images.shape
        img     = np.empty((len(analyzers), sh[1], sh[2]))
        for ind, analyzer in enumerate(analyzers):
            analyzer.integrate(self.images, img)
        return img


class AnalyzerA:
    def __init__(self, id):
        self.id = id

    def integrate(self, images, spectra):
        spectra[self.id] = np.sum(images, axis = 0)



# scans_a = []
# scans_b = []
# for i in range(S):
#     n = int(N / S)
#     scans_a.append( A(images[i * n:(i+1)*n], spectra[i * n:(i+1)*n]) )
#     scans_b.append(B(int(N/S), D1, D2, None))
#
# scans_a = np.array(scans_a)
# scans_b = np.array(scans_b)
#
# analyzers_a = []
# for i in range(4):
#     analyzers_a.append(AnalyzerA(i))
# analyzers_a = np.array(analyzers_a)
#
#
# def analyse(images):
#     np.sum(images, axis = 1)
#
def novfunc_a(scan):
    print(scan)
    # for analyzer in analyzers:
    #     scan.get_spectrum(analyzer)
#
# def novfunc_b(scans, analyzers):
#     for scan in scans:
#         scan.get_spectrum(analyzers)


t1 = timeit.Timer('run_pool()', "from __main__ import run_pool")
# t2 = timeit.Timer('novfunc_b(scans_b, analyzers_a)', "from __main__ import novfunc_b, scans_b, analyzers_a")
# # t4 = timeit.Timer('nonvfunc(scans_b)', "from __main__ import nonvfunc, scans_b")
#
print(t1.timeit(1))
# print(t2.timeit(1))
#print(t2.timeit(1))
# print(t3.timeit(500))
# print(t4.timeit(500))
