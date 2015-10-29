from abc import ABCMeta, abstractmethod
import numpy as np
import os

from uuid import uuid4

class BaseLikelihoodModel(object):

    __metaclass__ = ABCMeta

    def __init__(self, tardis_model, log_fname, spec_dir=None):
        self.tardis_model = tardis_model
        self.log_fname = log_fname
        self.spec_dir = spec_dir

    @abstractmethod
    def transform(self, *params):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def calculate_priors(self, *params):
        raise NotImplementedError

    def _write_log(self, uid, params, transformed_params, loglikelihood,
                   log_properties=[]):
        with open(self.log_fname, 'a') as fh:
            fh.write(' '.join(map(
                str, [uid] + list(params) + list(transformed_params) +
                     [loglikelihood] + log_properties)) + '\n')


    def __call__(self, *args, **kwargs):

        transformed_params = self.transform(*args)
        priors = self.calculate_priors(*transformed_params)

        uid = str(uuid4())

        if np.isinf(priors):
            loglikelihood = -0.5 * np.inf
        else:
            loglikelihood = self.tardis_model.evaluate(*transformed_params)
            if self.spec_dir is not None:
                spec_fname = os.path.join(
                        self.spec_dir, 'dalek_{0}_spec.txt'.format(uid))
                self.tardis_model[1].save_current_spectrum(spec_fname)



        self._write_log(uid, args, transformed_params, loglikelihood,
                        kwargs.get('log_properties', []))

        properties_dict = dict(uid=uid, transformed_params=transformed_params)
        return loglikelihood, properties_dict
