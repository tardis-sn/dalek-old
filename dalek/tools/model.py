import numpy as np

from dalek.tools.base import Link
from dalek.wrapper.tardis_wrapper import TardisWrapper
from astropy import units as u

class DummyException(Exception):
    pass


class Tardis(Link):
    inputs = ('parameters', 'uuid',)
    outputs = ('model',)

    def __init__(self, wrapper):
        if not isinstance(wrapper, TardisWrapper):
            raise ValueError(
                f"expected an instance of TardisWrapper, got: {str(type(wrapper))}"
            )
        self._wrapper = wrapper

    def calculate(self, parameters, uuid):

        def apply_config(config):
            for k, v in parameters.items():
                config.set_config_item(k, v)
            return config

        mdl = self._wrapper(apply_config, log_name=uuid)
        return mdl


class DummyTardis(Link):
    inputs = ('parameters', 'uuid',)
    outputs = ('model',)

    def __init__(self, wrapper):
        if not isinstance(wrapper, TardisWrapper):
            raise ValueError(
                f"expected an instance of TardisWrapper, got: {str(type(wrapper))}"
            )
        self._wrapper = wrapper

    def calculate(self, parameters, uuid):

        values = {}

        def apply_config(config):
            values['nu_max'] = config.spectrum[0].to(u.Hz, u.spectral()).value
            values['nu_min'] = config.spectrum[1].to(u.Hz, u.spectral()).value
            values['tos'] = config.supernova.time_explosion.cgs
            raise DummyException

        try:
            mdl = self._wrapper(apply_config, log_name=uuid)
        except DummyException:
            class DummyObject(object):
                pass
            mdl = DummyObject()
            mdl.runner = lambda: DummyObject()
        setattr(
                mdl.runner, 'virt_packet_nus',
                np.random.random(100000) *
                (values['nu_max'] - values['nu_min']) + values['nu_min'])
        setattr(
                mdl.runner, 'virt_packet_energies',
                np.random.random(100000))
        setattr(mdl.runner, 'time_of_simulation', values['tos'])
        return mdl
