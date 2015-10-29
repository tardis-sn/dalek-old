import pytest
from dalek.models.tardis import assemble_tardis_model, assemble_tardis_model_tinner

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

def test_assemble_tardis_model():
    pass