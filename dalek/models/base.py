import copy

from tardis.io.config_reader import ConfigurationNameSpace, Configuration
from tardis import run_tardis, model, simulation, atomic
from astropy import units as u, constants as const

from dalek.base.simulation import TinnerSimulation

from scipy import ndimage, interpolate

from astropy.modeling import Model, Parameter
import numpy as np
from collections import OrderedDict

class TARDISModelMixin(Model):
    inputs = tuple()
    outputs = ('packet_nu', 'packet_energy', 'virtual_nu', 'virtual_energy',
               'param_name', 'param_value')

    def __init__(self, config_name_space, **kwargs):
        self.config_name_space = config_name_space
        self.atom_data = atomic.AtomData.from_hdf5(config_name_space.atom_data)
        super(TARDISModelMixin, self).__init__(**kwargs)

    def _get_config_from_args(self, args):
        config_name_space = copy.deepcopy(self.config_name_space)
        for i, param_value in enumerate(args):
            param_value = np.squeeze(param_value)
            config_name_space.set_config_item(
                self.convert_param_dict.values()[i], param_value)
        return Configuration.from_config_dict(config_name_space,
                                                validate=False,
                                                atom_data=self.atom_data)

    def evaluate(self, *args, **kwargs):
        config = self._get_config_from_args(args)
        radial1d_mdl = model.Radial1DModel(config)

        simulation.run_radial1d(radial1d_mdl)
        runner = radial1d_mdl.runner

        param_names = ['t_inner']
        param_values = [radial1d_mdl.t_inner]
        self.mdl = radial1d_mdl
        return (runner.emitted_packet_nu,
                runner.emitted_packet_luminosity,
                runner.virt_packet_nus * u.Hz,
                (runner.virt_packet_energies /
                 runner.time_of_simulation),
                param_names, param_values)


class TARDISTinnerModelMixin(TARDISModelMixin):

    def evaluate(self, *args, **kwargs):
        config = self._get_config_from_args(args[:-1])

        t_inner = u.Quantity(args[-1], u.K)

        radial1d_mdl = model.Radial1DModel(config)

        simulation = TinnerSimulation(config)

        simulation.run_simulation(radial1d_mdl, t_inner)

        runner = simulation.runner

        param_names = ['t_inner']
        param_values = [radial1d_mdl.t_inner]
        self.mdl = radial1d_mdl
        return (runner.emitted_packet_nu,
                runner.emitted_packet_luminosity,
                runner.virt_packet_nus * u.Hz,
                (runner.virt_packet_energies /
                 runner.time_of_simulation),
                param_names, param_values)


def _convert_param_names(param_names):
    """

    Parameters
    ----------
    param_names: ~list of ~str

    Returns
    -------

    """
    short_param_names = []
    for param_name in param_names:
        if param_name.split('.')[-1].startswith('item'):
            short_param_name = "{0}_{1}".format(
                param_name.split('.')[-2],
                param_name.split('.')[-1].replace('item', ''))
        else:
            short_param_name = param_name.split('.')[-1]
        short_param_names.append(short_param_name)


    if len(set(short_param_names)) != len(param_names):
        raise ValueError('Paramnames are not unique')

    return OrderedDict(zip(short_param_names, param_names))


def _generate_param_class_dict(fname, param_names):
    """
    Generate the parameter and class dictionaries for the Model
    Parameters
    ----------
    fname: ~str
    param_names: ~list of ~str

    Returns
    -------

    """

    config = ConfigurationNameSpace.from_yaml(fname)
    param_dict = {}
    short_param_name_dict = _convert_param_names(param_names)

    class_dict = {'convert_param_dict': short_param_name_dict}
    for key in short_param_name_dict:
        try:
            value = config.get_config_item(short_param_name_dict[key])
        except KeyError:
            raise ValueError('{0} is not a valid parameter'.format(key))
        class_dict[key] = Parameter()
        param_dict[key] = getattr(value, 'value', value)

    return class_dict, param_dict, config

def assemble_tardis_model(fname, param_names):
    """
    Assemble a TARDIS model with given Parameter names

    Parameters
    ----------
    fname
    param_names

    Returns
    -------

    """

    class_dict, param_dict, config = _generate_param_class_dict(
        fname, param_names)

    class_dict['__init__'] = TARDISModelMixin.__init__

    simple_model = type('SimpleTARDISModel', (TARDISModelMixin,), class_dict)

    return simple_model(config, **param_dict)





def assemble_tardis_model_tinner(fname, param_names):
    """

    Parameters
    ----------
    fname
    param_names

    Returns
    -------

    """

    class_dict, param_dict, config = _generate_param_class_dict(
        fname, param_names)

    param_dict['t_inner'] = 10000
    class_dict['t_inner'] = Parameter()


    class_dict['__init__'] = TARDISTinnerModelMixin.__init__

    simple_model = type('SimpleTARDISModel', (TARDISTinnerModelMixin,),
                        class_dict)

    return simple_model(config, **param_dict)
