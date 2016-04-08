import os
import numpy as np
from astropy import units as u, constants as const
# Some helper functions

def intensity_black_body_wavelength(wavelength, T):
    wavelength = u.Quantity(wavelength, u.angstrom)
    T = u.Quantity(T, u.K)
    f = ((8 * np.pi * const.h * const.c) / wavelength**5)
    return f / (np.exp((const.h * const.c)/(wavelength * const.k_B * T)) - 1)

def bin_center_to_edge(bin_center):
    hdiff = 0.5 * np.diff(bin_center)
    hdiff = np.hstack((-hdiff[0], hdiff, hdiff[-1]))
    return np.hstack((
        bin_center[0],
        bin_center)) + hdiff

def bin_edge_to_center(bin_edge):
    return 0.5 * (bin_edge[:-1] + bin_edge[1:] )

def set_engines_cpu_affinity():
    import sys
    if sys.platform.startswith('linux'):
        try:
            import psutil
        except ImportError:
            print 'psutil not available - can not set CPU affinity'
        else:
            from multiprocessing import cpu_count
            p = psutil.Process(os.getpid())
            p.cpu_affinity(range(cpu_count()))

