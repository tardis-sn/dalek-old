from collections import OrderedDict

import numpy as np
from astropy.modeling import Model

from astropy import units as u, constants as const

def intensity_black_body_wavelength(wavelength, T):
    wavelength = u.Quantity(wavelength, u.angstrom)
    T = u.Quantity(T, u.K)
    pref = ((8 * np.pi * const.h * const.c) / wavelength**5)
    return pref / (np.exp((const.h * const.c)/(wavelength * const.k_B * T)) - 1)



class SimpleTARDISUncertaintyModel(Model):
    inputs = ('packet_nu', 'packet_energy', 'virtual_nu', 'virtual_energy',
              'param_names', 'param_values')
    outputs = ('wavelength', 'luminosity', 'uncertainty', 'param_names', 'param_values')


    def __init__(self, observed_wavelength, mode='virtual',
                 virtual_uncertainty_scaling=5.):
        self.observed_wavelength = observed_wavelength
        self.wavelength_bins = self._generate_bins(observed_wavelength)
        self.mode = mode
        self.virtual_uncertainty_scaling = virtual_uncertainty_scaling
        super(SimpleTARDISUncertaintyModel, self).__init__()

    @staticmethod
    def _generate_bins(observed_wavelength):
        hdiff = 0.5 * np.diff(observed_wavelength)
        hdiff = np.hstack((-hdiff[0], hdiff, hdiff[-1]))
        return np.hstack((observed_wavelength[0], observed_wavelength)) + hdiff

    def evaluate(self, packet_nu, packet_energy, virtual_nu, virtual_energy,
                 param_names, param_values):
        packet_lambda = packet_nu.to(u.angstrom, u.spectral())
        bin_counts = np.histogram(packet_lambda, bins=self.wavelength_bins)[0]

        uncertainty = (np.sqrt(bin_counts) * np.mean(packet_energy)
                       / np.diff(self.wavelength_bins))

        if self.mode == 'normal':
            luminosity = np.histogram(packet_lambda,
                          weights=packet_energy,
                          bins=self.wavelength_bins)[0]
        elif self.mode == 'virtual':
            virtual_packet_lambda = virtual_nu.to(u.angstrom, u.spectral())
            luminosity = np.histogram(virtual_packet_lambda,
                          weights=virtual_energy,
                          bins=self.wavelength_bins)[0]
            uncertainty /= self.virtual_uncertainty_scaling

        luminosity_density = luminosity / np.diff(self.wavelength_bins)

        self.luminosity_density = luminosity_density
        self.uncertainty = uncertainty.value
        return (self.observed_wavelength, luminosity_density, uncertainty.value,
                param_names, param_values)

    def save_current_spectrum(self, fname):
        np.savetxt(fname, zip(self.observed_wavelength, self.luminosity_density,
                              self.uncertainty))



class NormRedSpectrum(Model):
    inputs = ('wavelength', 'flux', 'uncertainty', 'param_names', 'param_values')
    outputs = ('wavelength', 'flux', 'uncertainty', 'param_names', 'param_values')

    def __init__(self, norm_start=6300):
        super(NormRedSpectrum, self).__init__()
        self.norm_start = norm_start

    def evaluate(self, wavelength, flux, uncertainty, param_names, param_values):
        param_dict = OrderedDict(zip(param_names, param_values))

        norm_start_idx = wavelength.searchsorted(self.norm_start)
        norm_curve = intensity_black_body_wavelength(
            wavelength[norm_start_idx:], param_dict['t_inner'])
        norm_curve /= norm_curve[0]

        normed_flux = flux.copy()
        normed_flux[norm_start_idx:] *= norm_curve
        normed_uncertainty = uncertainty.copy()
        normed_uncertainty[norm_start_idx:] *= norm_curve
        return (wavelength, normed_flux, normed_uncertainty,
                param_names, param_values)

class NormUniformSmooth(Model):
    inputs = ('wavelength', 'flux', 'uncertainty', 'param_names', 'param_values')
    outputs = ('wavelength', 'flux', 'uncertainty', 'param_names', 'param_values')

    def __init__(self, smoothing_scale=100.):
        self.smoothing_scale = smoothing_scale
        super(NormUniformSmooth, self).__init__()

    def evaluate(self, wavelength, flux, uncertainty, param_names, param_values):
        flux_filtered = ndimage.uniform_filter1d(flux, self.smoothing_scale)
        flux_normalized = flux / flux_filtered - 1.
        flux_normalized -= np.mean(flux_normalized)
        uncertainty_normalized = uncertainty / flux_filtered

        return wavelength, flux_normalized, uncertainty_normalized, param_names, param_values



class LogLikelihood(Model):
    inputs = ('wavelength', 'flux', 'uncertainty', 'param_names',
              'param_values')
    outputs = ('loglikelihood',)

    spec_fname = None

    def __init__(self, observed_wavelength, observed_flux,
                 observed_uncertainty, wavelength_start=0.,
                 wavelength_end=np.inf):
        self.observed_wavelength = observed_wavelength
        self.observed_flux = observed_flux
        self.observed_uncertainty = observed_uncertainty

        self.wavelength_slice = slice(
            self.observed_wavelength.searchsorted(wavelength_start),
            self.observed_wavelength.searchsorted(wavelength_end))
        super(LogLikelihood, self).__init__()

    def save_current_spectrum(self, fname):
        np.savetxt(fname, zip(
            self.current_wavelength, self.current_flux,
            self.current_uncertainty))

    def evaluate(self, wavelength, flux, uncertainty, param_names,
                 param_values):
        self.current_wavelength = wavelength
        self.current_flux = flux
        self.current_uncertainty = uncertainty
        return (-0.5 * np.sum((self.observed_flux[self.wavelength_slice] - flux[self.wavelength_slice])**2 /
                              (uncertainty[self.wavelength_slice]**2 + self.observed_uncertainty[self.wavelength_slice]**2)))



class SSum(Model):
    inputs = ('wavelength', 'flux', 'uncertainty', 'param_names',
              'param_values')
    outputs = ('loglikelihood',)

    spec_fname = None

    def __init__(self, observed_wavelength, observed_flux,
                 observed_uncertainty, wavelength_start=0.,
                 wavelength_end=np.inf):
        self.observed_wavelength = observed_wavelength
        self.observed_flux = observed_flux
        self.observed_uncertainty = observed_uncertainty

        self.wavelength_slice = slice(
            self.observed_wavelength.searchsorted(wavelength_start),
            self.observed_wavelength.searchsorted(wavelength_end))
        super(SSum, self).__init__()

    def save_current_spectrum(self, fname):
        np.savetxt(fname, zip(
            self.current_wavelength, self.current_flux,
            self.current_uncertainty))

    def evaluate(self, wavelength, flux, uncertainty, param_names,
                 param_values):
        self.current_wavelength = wavelength
        self.current_flux = flux
        self.current_uncertainty = uncertainty
        return -0.5 * np.sum(
            (self.observed_flux[self.wavelength_slice] -
             flux[self.wavelength_slice])**2)
