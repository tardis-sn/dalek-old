
# coding: utf-8

# In[54]:

import os
import logging

from uuid import uuid4
from copy import deepcopy

from tardis.atomic import AtomData
from tardis.model import Radial1DModel
from tardis.simulation import run_radial1d
from tardis.io.config_reader import Configuration, ConfigurationNameSpace

from dalek.base.simulation import TinnerSimulation

class TardisWrapper(object):

    def __init__(self, config_fname, atom_data=None, log_dir='./logs/'):
        self._log_dir = log_dir
        self.set_logger('startup')
        self._config = ConfigurationNameSpace.from_yaml(config_fname)
        if atom_data is None:
            self._atom_data = AtomData.from_hdf5(self._config.atom_data)
        else:
            self._atom_data = atom_data


    def __call__(self, callback, log_name=None):
        if log_name is None:
            log_name = uuid4()
        self.set_logger(log_name)
        config = self._generate_config(callback)
        self.model = self.run_tardis(config)
        return self.model

    def _generate_config(self, callback):
        config_ns = callback(self.config)
        return Configuration.from_config_dict(
                config_ns,
                validate=False,
                atom_data=self.atom_data)

    def set_logger(self, name):
        filename = os.path.join(self._log_dir, 'tardis_{}.log'.format(name))
        self._set_logger(filename)

    def _set_logger(self, filename):
        tardis_logger = logging.getLogger('tardis')
        tardis_logger.setLevel(logging.INFO)
        fileHandler = logging.FileHandler(filename)
        tardis_logger.handlers = [fileHandler]

    def run_tardis(self, config):
        mdl = Radial1DModel(config)
        run_radial1d(mdl)
        return mdl


    @property
    def atom_data(self):
        return deepcopy(self._atom_data)

    @property
    def config(self):
        return deepcopy(self._config)


class TInnerWrapper(TardisWrapper):

    def run_tardis(self, config):
        mdl = Radial1DModel(config)
        t_inner = config.get_config_item('plasma.t_inner')
        simulation = TinnerSimulation(config)
        simulation.run_simulation(mdl, t_inner)
        mdl.runner = simulation.runner
        return mdl

