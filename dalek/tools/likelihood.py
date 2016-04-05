import numpy as np

from dalek.tools.base import Link


# class BaseLikelihoodModel(object):
#
#     def __init__(self, tardis_model, log_fname, spec_dir=None):
#         self.tardis_model = tardis_model
#         self.log_fname = log_fname
#         self.spec_dir = spec_dir
#
#     def __call__(self, *args, **kwargs):
#
#         transformed_params = self.transform(*args)
#         priors = self.calculate_priors(*transformed_params)
#
#         if np.isinf(priors):
#             loglikelihood = -0.5 * np.inf
#         else:
#             loglikelihood = self.tardis_model.evaluate(*transformed_params)
#
#         properties_dict = dict(transformed_params=transformed_params)
#         return loglikelihood, properties_dict

class SSum(Link):
    inputs = ('flux',)
    outputs = ('loglikelihood',)

    def __init__(self, wl, flux, start=0, end=np.inf):
        if len(wl) == len(flux) + 1:
            # convert bin edges to bin centers
            wl = (wl[1:] + wl[:-1]) / 2
        self._slice = slice(
                wl.searchsorted(start),
                wl.searchsorted(end) + 1
                )
        self._observed_flux = flux.to('erg / ( Angstrom cm2 s )')

    def calculate(self, flux):
        return -0.5 * np.sum(
                (self._observed_flux[self._slice] -
                flux[self._slice])**2)

