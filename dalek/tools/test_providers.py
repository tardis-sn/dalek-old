import pytest
import numpy as np
from astropy import units as u

from dalek.tools.providers import (
        PacketProvider, VirtualPacketProvider,
        Luminosity, VirtualLuminosity,
        Flux,
        )
from dalek.tools.base import Chain


@pytest.fixture
def input_dict(model):
    return {
            'model': model
            }


@pytest.fixture
def vmodel(model):
    if not hasattr(model.runner, 'virt_packet_nus'):
        pytest.skip(reason="No virtual data present in model")
    return model

@pytest.fixture
def bins(model):
    return model.tardis_config.spectrum.frequency.to(
            u.angstrom, u.spectral())[::-1].value


def test_packet_provider(input_dict, model):
    # print pprovider(input_dict)
    pprovider = PacketProvider()
    result = pprovider(input_dict)
    assert np.all(
            result['packet_energy'] ==
            model.runner.emitted_packet_luminosity)
    assert np.all(
            result['packet_nu'] ==
            model.runner.emitted_packet_nu)
    assert result['packet_nu'].unit.is_equivalent('Hz')
    assert result['packet_energy'].unit.is_equivalent('erg/s')


def test_vpacket_provider(input_dict, vmodel):
    vprovider = VirtualPacketProvider()
    result = vprovider({'model': vmodel})
    assert np.all(
            result['virtual_packet_energy'] ==
            vmodel.runner.virt_packet_energies * u.erg /
            vmodel.runner.time_of_simulation)
    assert np.all(
            result['virtual_packet_nu'] ==
            vmodel.runner.virt_packet_nus * u.Hz)
    assert result['virtual_packet_nu'].unit.is_equivalent('Hz')
    assert result['virtual_packet_energy'].unit.is_equivalent('erg/s')


def test_luminosity(input_dict, model, bins):
    luminosity = Luminosity(bins * u.angstrom)
    lum_density = np.histogram(
            model.runner.emitted_packet_nu.to(u.angstrom, u.spectral()),
            weights=model.runner.emitted_packet_luminosity,
            bins=bins)[0] / np.diff(bins)

    obtained = luminosity(PacketProvider()({'model': model,}))['luminosity']
    np.testing.assert_allclose(
            obtained.value,
            lum_density)
    assert obtained.unit.is_equivalent('erg/ (angstrom s)')


def test_vluminosity(input_dict, vmodel, bins):
    vluminosity = VirtualLuminosity(bins * u.angstrom)
    lum_density = np.histogram(
            (vmodel.runner.virt_packet_nus*u.Hz).to(u.angstrom, u.spectral()),
            weights=vmodel.runner.virt_packet_energies /
            vmodel.runner.time_of_simulation,
            bins=bins)[0] / np.diff(bins)

    obtained = vluminosity(VirtualPacketProvider()({'model': vmodel,}))['luminosity']
    np.testing.assert_allclose(obtained.value,
        lum_density)
    assert obtained.unit.is_equivalent('erg/ (angstrom s)')


def test_flux(model, bins):
    flux_chain = Chain(PacketProvider(), Luminosity(bins * u.angstrom), Flux())
    obtained = flux_chain({'model': model})['flux']
    assert obtained.unit.is_equivalent('erg / (s Angstrom cm2)')
