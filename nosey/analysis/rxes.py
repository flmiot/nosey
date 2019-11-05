import re
import h5py
import logging
import numpy as np
import scipy.interpolate as interp
import scipy.optimize as optim

import matplotlib.pyplot as plt

MYTHEN_MASK = slice(0, 1140)


def getRXESmap(scans, p0=400, e0=7649, dE_mythen=0.195,
               normalize_AUC=1000, show_corrected=False):
    """ Requires same type energy ascans """

    for scan in scans:

        # RXES 1: Incident - Emission (omega Omega)
        cmd = scan['command'][0].decode("utf-8")
        e_0, e_1, steps = re.findall(
            r'\S+\s\S+\s([\d.]+)\s([\d.]+)\s(\d+)', cmd)[0]
        e_0, e_1, steps = float(e_0), float(e_1), int(steps) + 1

        # *energies_x* is the incoming/excitation energy
        energies_x = np.array(list([float(v) for v in scan['energy']]))
        sh = scan['m_raw'].shape
        e_min = float(scan['ceout']) - (sh[1] - p0) * dE_mythen
        e_max = float(scan['ceout']) + p0 * dE_mythen

        # *energies_y*
        energies_y = np.linspace(e_max, e_min, sh[1])
        summend_maps.append(scan['m_raw'])

        # RXES 2: Incident - Incident-Emission (omega Omega-omega)
        stepsize_y = (np.max(energies_y)-np.min(energies_y))/len(energies_y)
        energy_loss_min = e_0 - np.max(energies_y)
        energy_loss_max = e_1 - np.min(energies_y)
        l = int((energy_loss_max - energy_loss_min)/stepsize_y)
        energy_loss_axis = np.linspace(energy_loss_max, energy_loss_min, l)
        energy_loss_map = np.empty((sh[0], l))

        for idx, row in enumerate(scan['m_raw']):

            p = interp.interp1d(
                x = energies_x[idx] - energies_y,
                y = row,
                bounds_error = False)
            energy_loss_map[idx] = p(energy_loss_axis)

        summend_maps_energy_loss.append(energy_loss_map)

    d = {
        'Omega'         : energies_x,
        'omega'         : energies_y,
        'Omega-omega'   : energy_loss_axis,
        'mapOo'         : np.nansum(summend_maps, axis = 0),
        'mapOO-o'       : np.nansum(summend_maps_energy_loss, axis = 0)
        }

    if show_corrected:
        plt.figure()
        plt.imshow(d['mapOo'].T, aspect = 'auto')
        plt.figure()
        plt.imshow(d['mapOO-o'].T, aspect = 'auto')
        plt.show()

    return d


def overlayRXESmaps(maps):
    """ Requires maps of same shape. Will shift maps along first dimension to
        overlap them according to their energy_axis """

    overlayed_maps = []
    overlayed_maps_el = []
    new_energy_axis = np.mean([d['omega'] for d in maps], axis = 0)
    new_energy_axis_el = np.mean([d['Omega-omega'] for d in maps], axis = 0)

    for m in maps:
        shifted = np.empty(m['mapOo'].shape)
        shifted_el = np.empty(m['mapOO-o'].shape)

        # Oo
        for idx, row in enumerate(m['mapOo']):
            axis = m['omega']
            p = interp.interp1d(
                x = axis,
                y = row,
                bounds_error = False)

            shifted[idx] = p(new_energy_axis)

        # OO-o
        for idx, row in enumerate(m['mapOO-o']):
            axis = m['Omega-omega']
            p_el = interp.interp1d(
                x = axis,
                y = row,
                bounds_error = False)

            shifted_el[idx] = p_el(new_energy_axis_el)

        overlayed_maps.append(shifted)
        overlayed_maps_el.append(shifted_el)

    d = {
        'Omega'         : maps[0]['Omega'],
        'omega'         : new_energy_axis,
        'Omega-omega'   : new_energy_axis_el,
        'mapOo'         : np.mean(overlayed_maps, axis = 0),
        'mapOO-o'       : np.mean(overlayed_maps_el, axis = 0),
        }

    return d

def normalizeRXESmaps(d, n, e, show_plots = False):
    """
    """

    d = dict(d)
    n = dict(n)
    d['sliceOo'] = d['mapOo'][:, np.argmin(np.abs(d['omega'] - e))].copy()
    n['sliceOo'] = n['mapOo'][:, np.argmin(np.abs(n['omega'] - e))].copy()

    # [1]
    def reBinData(d, n):
        """ Rebin XANES data to match the (coarse) normalization scan """
        e_step = np.mean(np.diff(n['Omega']))

        e0, e1 = np.min(d['Omega']), np.max(d['Omega'])
        i0 = np.argmin(np.abs(n['Omega'] - e0))
        i1 = np.argmin(np.abs(n['Omega'] - e1))

        binned_slice = []
        binned_energies = []
        for e in n['Omega'][i0:i1+1]:
            ek0 = e - e_step/2
            ek1 = e + e_step/2
            k0 = np.argmin(np.abs(d['Omega'] - ek0))
            k1 = np.argmin(np.abs(d['Omega'] - ek1))
            binned_slice.append(np.nanmean(d['sliceOo'][k0:k1+1]))
            binned_energies.append(np.mean([ek0, ek1]))

        return binned_energies, np.array(binned_slice)
        # bin_number  = (np.max(d['Omega'])-np.min(d['Omega'])) / energy_step
        # bin_interval = int(len(d['Omega']) / bin_number)
        # print(energy_step, bin_interval, bin_number)
        # values = np.arange(len(d['Omega']))[::bin_interval]
        # x  = np.array([d['Omega'][i:i+bin_interval].mean() for i in values])
        # y  = np.array([d['sliceOo'][i:i+bin_interval].mean() for i in values])
        # return x, y

        #
        #
        # wsize = int((n['Omega'][1] - n['Omega'][0]) / (d['Omega'][1] - d['Omega'][0])) * 2
        # cumsum = np.cumsum(np.insert(d['sliceOo'], 0, 0))
        # slice = (cumsum[wsize:] - cumsum[:-wsize]) / float(wsize)
        # cumsum = np.cumsum(np.insert(d['Omega'], 0, 0))
        # energies = (cumsum[wsize:] - cumsum[:-wsize]) / float(wsize)
        # return energies, slice

    d['Omega_binned'], d['sliceOo_binned'] = reBinData(d, n)

    f_data = interp.interp1d(
        d['Omega_binned'],
        d['sliceOo_binned'],
        bounds_error = False)
    f_norm = interp.interp1d(
        n['Omega'],
        n['sliceOo'],
        bounds_error = False)

    def modelFunction(energy, scale, shift):
        return scale * f_norm(energy - shift)

    e0, e1 = np.min(d['Omega_binned']), np.max(d['Omega_binned'])
    i0, i1 = np.argmin(np.abs(n['Omega'] - e0)), np.argmin(np.abs(n['Omega'] - e1))

    while e0 >= n['Omega'][i0]:
        i0 += 1
    while e1 <= n['Omega'][i1]:
        i1 -= 1

    guess = [np.nanmax(n['sliceOo']) / np.nanmax(d['sliceOo_binned']), 0.0]
    popt, pcov = optim.curve_fit(
        f = modelFunction,
        xdata = n['Omega'][i0:i1],
        ydata = f_data(n['Omega'][i0:i1]),
        p0 = guess)

    factor1 = 1 / popt[0]

    # [2]
    post_e0, post_e1 = 7900, 8100
    post_i0 = np.argmin(np.abs(n['Omega'] - post_e0))
    post_i1 = np.argmin(np.abs(n['Omega']  - post_e1))
    post_edge_level = np.mean(n['sliceOo'][post_i0:post_i1])

    factor2 = 1 / post_edge_level

    d['mapOo'] *= factor1 * factor2
    d['mapOO-o'] *= factor1 * factor2
    d['mapOo'] += 0.001
    d['mapOO-o'] += 0.001

    if show_plots:
        plt.figure()
        plt.plot(n['Omega'], n['sliceOo'], label = 'normalization data')
        plt.plot(d['Omega_binned'] - popt[1], d['sliceOo_binned'] * factor1, label = 'fitted data (binned)')
        plt.plot(d['Omega']- popt[1], d['sliceOo'] * factor1, label = 'fitted data')
        plt.legend()
        plt.figure()
        plt.plot(n['Omega'], n['sliceOo'] * factor2, label = 'normalization data')
        plt.plot(d['Omega'], d['sliceOo'] * factor1 * factor2, label = 'fitted data')
        plt.legend()
        plt.figure()
        plt.imshow(d['mapOo'], aspect = 'auto')
        plt.figure()
        plt.imshow(d['mapOO-o'], aspect = 'auto')
        plt.show()

    return d


def subtractRXESmaps(a, b, vrange = None):
    """ """

    # O-o
    o0 = np.max([np.min(a['omega']), np.min(b['omega'])])
    o1 = np.min([np.max(a['omega']), np.max(b['omega'])])
    O0 = np.max([np.min(a['Omega']), np.min(b['Omega'])])
    O1 = np.min([np.max(a['Omega']), np.max(b['Omega'])])
    points_omega = np.min([len(a['omega']), len(b['omega'])])
    points_Omega = np.min([len(a['Omega']), len(b['Omega'])])
    omega = np.linspace(o1, o0, points_omega)
    Omega = np.linspace(O0, O1, points_Omega)

    diff = np.empty((points_Omega, points_omega))
    for idx, O in zip(range(len(Omega)), Omega):
        ia = np.argmin(np.abs(a['Omega'] - O))
        ib = np.argmin(np.abs(b['Omega'] - O))
        fa = interp.interp1d(a['omega'], a['mapOo'][ia])
        fb = interp.interp1d(b['omega'], b['mapOo'][ib])
        diff[idx] = fa(omega) -fb(omega)

    # OO-o
    o0 = np.max([np.min(a['Omega-omega']), np.min(b['Omega-omega'])])
    o1 = np.min([np.max(a['Omega-omega']), np.max(b['Omega-omega'])])
    points_omega = np.min([len(a['Omega-omega']), len(b['Omega-omega'])])
    omegaOOo = np.linspace(o1, o0, points_omega)

    diff_OOo = np.empty((points_Omega, points_omega))
    for idx in range(len(Omega)):
        fa = interp.interp1d(a['Omega-omega'], a['mapOO-o'][idx])
        fb = interp.interp1d(b['Omega-omega'], b['mapOO-o'][idx])
        diff_OOo[idx] = fa(omegaOOo) -fb(omegaOOo)

    if vrange:
        diff -= np.nanmin(diff)
        diff /= np.nanmax(diff)
        diff *= (vrange[1]-vrange[0])
        diff += vrange[0]

        diff_OOo -= np.nanmin(diff_OOo)
        diff_OOo /= np.nanmax(diff_OOo)
        diff_OOo *= (vrange[1]-vrange[0])
        diff_OOo += vrange[0]


    plt.imshow(diff_OOo)
    plt.show()

    d = {
        'Omega'         : Omega,
        'omega'         : omega,
        'Omega-omega'   : omegaOOo,
        'mapOo'         : diff,
        'mapOO-o'       : diff_OOo
    }

    return d



def binData(x, y, bin_number = 2):
    values = np.arange(len(x))[::bin_number]
    binned_x  = np.array([x[i:i+bin_number].mean() for i in values])
    binned_y  = np.array([y[i:i+bin_number].mean() for i in values])
    return binned_x, binned_y

def binData2D(axis, array, bin_number = 2):
    """ Will be binned along second dimension """
    values = np.arange(array.shape[1])[::bin_number]
    binned_axis = np.array([axis[i:i+bin_number].mean() for i in values])
    binned_array = np.empty((array.shape[0], len(binned_axis)))
    for ind, row in enumerate(array):
        binned_array[ind] = np.array([row[i:i+bin_number].mean() for i in values])
    return binned_axis, binned_array
