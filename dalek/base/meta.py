# coding: utf-8
import os
import pandas as pd
from dalek.wrapper import SafeHDFStore
import warnings
import tables

class MetaContainer(object):
    """
    Class to control storing of metainformation

    Parameters
    -----
        path: string
            Absolute path to output .h5 file
        summary_data: dictionary-like object
            Additional information that should be saved.
            For example dalek_version, tardis_version, time, ranks, iterations

    """
    def __init__(self, path, summary_data=None):
        self._path, self._file = os.path.split(path)
        self.open = False
        if summary_data is not None:
            self._write_summary(summary_data)

    def _write_summary(self, data):
        '''
        Write summary_data to .h5 file.
        '''
        # TODO: proper dictionary to pd.Series parsing
        with self as store:
            if 'overview' not in store.keys():
                store.put('overview', pd.Series(data.values(), index=data.keys()))

    def __enter__(self):
        '''
        Wrapper function to allow

        with MetaContainer as store:
            <code>
        '''
        if not self.open:
            self.open = True
            self.store = SafeHDFStore(os.path.join(self._path, self._file))
        return self.store

    def __exit__(self, type, value, traceback):
        '''
        close store after 'with'
        '''
        if self.open:
            self.store.__exit__(type, value, traceback)
            self.open = False
        return



class MetaInformation(object):

    def __init__(self, uuid, rank, iteration, fitness, additional_data=None):
        self._uuid = uuid
        self._rank = rank
        self._iteration = iteration
        self._fitness = fitness
        self._additional_data = additional_data
        self._data = list()

    @classmethod
    def from_wrapper(cls, wrapper, parameter_dict):
        mdl = wrapper.model
        inst = cls(
                uuid=wrapper.uuid,
                rank=wrapper.rank,
                iteration=wrapper.iteration,
                fitness=wrapper.fitness,
                additional_data=parameter_dict)
        inst.add_data('spec',
                pd.Series(mdl.spectrum.luminosity_density_lambda))
        inst.add_data('spec_virt',
                pd.Series(mdl.spectrum_virtual.luminosity_density_lambda))
        inst.add_data('t_rads', pd.Series(mdl.t_rads))
        inst.add_data('ws', pd.Series(mdl.ws))
        return inst

    def add_data(self, name, data):
        self._data.append(name)
        setattr(self, '_' + name, data)

    def data_path(self, name=''):
        return 'data/{}/{}'.format(self._uuid, name)


    @property
    def run_details(self):
        res = {
                'rank': self._rank,
                'iteration': self._iteration,
                'uuid': str(self._uuid),
                'fitness': self._fitness,
                }
        try:
            for k,v in self._additional_data.items():
                res[k] = v
        except AttributeError:
            pass
        return res

    @property
    def details(self):
        return (pd.DataFrame.from_records([self.run_details]).
                    set_index(['iteration','rank']))


    def _save_data(self, store):
        warnings.simplefilter('ignore', tables.NaturalNameWarning)
        for d in self._data:
            getattr(self,'_' + d).to_hdf(store, self.data_path(d))


    def save(self, container):
        with container as store:
            self._save_data(store)
            store.append('run_table', self.details)
