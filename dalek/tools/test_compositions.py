import pytest
import numpy as np
from astropy import units as u

from dalek.util import bin_center_to_edge
from dalek.wrapper.tardis_wrapper import TardisWrapper
from dalek.tools.base import Chain
from dalek.tools.compositions import SimpleTardis
from dalek.tools.providers import RunInfo


@pytest.fixture
def artis_path():
    return "/home/stefan/projects/dalek/data/wrapper-test/aaflux_057.dat"


@pytest.fixture
def artisw(artis_path):
    wl, _ = np.loadtxt(artis_path, unpack=True)
    return bin_center_to_edge(wl) * u.angstrom


@pytest.fixture
def artisf(artis_path):
    _, artisf = np.loadtxt(artis_path, unpack=True)
    return artisf * u.erg / (u.cm**2) / u.angstrom / u.s


def test_tardis(config_path, log_path, artisw, artisf):
    wrapper = TardisWrapper(config_path, log_dir=log_path)

    parameters = {
            'model.abundances.o': 0.1,
            }

    chain = Chain(RunInfo(), SimpleTardis(wrapper, artisw, artisf))
    output = chain(
            {
                'parameters': parameters
                }
            )
    print(output['flux'])
