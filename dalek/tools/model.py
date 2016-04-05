from dalek.tools.base import Link
from dalek.wrapper.tardis_wrapper import TardisWrapper


class Tardis(Link):
    inputs = ('parameters', 'uuid',)
    outputs = ('model',)

    def __init__(self, wrapper):
        if not isinstance(wrapper, TardisWrapper):
            raise ValueError(
                    "expected an instance of TardisWrapper, got: {}".format(
                        str(type(wrapper)))
                    )
        self._wrapper = wrapper

    def calculate(self, parameters, uuid):

        def apply_config(config):
            for k, v in parameters.items():
                config.set_config_item(k, v)
            return config

        self._wrapper.set_logger(uuid)
        mdl = self._wrapper(apply_config)
        return mdl
