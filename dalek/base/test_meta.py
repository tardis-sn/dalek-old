import os
import pytest
import tempfile
from uuid import uuid4
import numpy as np
import pandas as pd

from dalek.base.meta import MetaContainer, MetaInformation

class DummyRadial1D(object):

    def __init__(self):
        class Spectrum(object):
            def __init__(self):
                self.luminosity_density_lambda = np.random.random(10000)
        self.t_rads = np.linspace(15000, 1000, 20)
        self.ws = np.random.random(20)
        self.spectrum = Spectrum()
        self.spectrum_virtual = Spectrum()

class DummyWrapper(object):

    def __init__(self):
        self.model = DummyRadial1D()
        self.uuid = uuid4()
        self.iteration = 1
        self.rank = 0
        self.fitness = 123

class TestMetaContainer(object):

    @classmethod
    @pytest.fixture(scope='class', autouse=True)
    def setup(self, request):
        self._file = tempfile.NamedTemporaryFile()
        self.container = MetaContainer(self._file.name)
        def fin():
            os.remove(self._file.name)
        request.addfinalizer(fin)

    def test_read_write(self):
        tmp = pd.Series(np.arange(10))
        with self.container as store:
            store['s'] = tmp
            print(store.filename)

        with self.container as store:
            print(store.filename)
            assert np.all(tmp==store['s'].values)
            del store['s']


class TestMetaInformation(object):

    @classmethod
    @pytest.fixture(scope='function', autouse=True)
    def setup(self, request):
        self._file = tempfile.NamedTemporaryFile()
        self.container = MetaContainer(self._file.name)

    @pytest.fixture(scope='class')
    def parameter_dict(self):
        return {
                'o': 0.1,
                'o_raw' : 0.01
                }


    def test_init(self):
        uuid = uuid4()
        instance = MetaInformation(uuid, 0,1,2,{})
        assert instance._rank == 0
        assert instance._iteration == 1
        assert instance._fitness == 2
        assert instance._additional_data == {}
        assert instance._uuid == uuid


    # @pytest.mark.skipif(True, reason='debug')
    def test_save(self, parameter_dict):
        wrapper = DummyWrapper()
        message = MetaInformation.from_wrapper(wrapper, parameter_dict)
        message.save(self.container)
        with self.container as store:
            diff = store['summary'].loc[1,0] == message.details.loc[1,0]
            assert diff.all()
            #print(store)
            #print(store.keys())
            #print(store['summary'])


    # @pytest.mark.skipif(True, reason='debug')
    def test_save_multiple(self, parameter_dict):
        wrapper = DummyWrapper()
        message = MetaInformation.from_wrapper(wrapper, parameter_dict)
        message.save(self.container)
        wrapper = DummyWrapper()
        wrapper.iteration = 2
        message2 = MetaInformation.from_wrapper(wrapper, parameter_dict)
        message2.save(self.container)
        with self.container as store:
            diff = store['summary'].loc[1,0] == message.details.loc[1,0]
            diff2 = store['summary'].loc[2,0] == message2.details.loc[2,0]
            assert diff.all()
            assert diff2.all()
            #print(store.keys())
            #print(store)
            #print(store.keys())
            #print(store['summary'])

