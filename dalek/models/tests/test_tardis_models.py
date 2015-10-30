import os

import pytest
from dalek.models import assemble_tardis_model, assemble_tardis_model_tinner

@pytest.fixture()
def parameter_names():
    return ['model.abundances.o',
    'model.abundances.si',
    'model.abundances.s',
    'model.abundances.ca',
    'model.abundances.fe',
    'model.abundances.co',
    'model.abundances.ni',
    'model.abundances.mg',
    'model.abundances.ti',
    'model.abundances.cr',
    'model.abundances.c',
    'supernova.luminosity_requested',
    'model.structure.velocity.item0']


@pytest.fixture
def tardis_artis_test_fname(data_path):
    return os.path.join(data_path, 'tardis_artis_fits.yml')

def test_assemble_tardis_model(tardis_artis_test_fname, parameter_names):
    mdl = assemble_tardis_model(tardis_artis_test_fname, parameter_names)

def test_assemble_tardis_tinner_model():
    pass