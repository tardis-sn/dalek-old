from astropy import units as u
from dalek.tools.base import Chain

from dalek.tools.model import Tardis
from dalek.tools.prior import Prior, CheckPrior
from dalek.tools.posterior import Posterior
from dalek.tools.providers import (
        VirtualPacketProvider,
        VirtualLuminosity,
        Flux,
        RunInfo
        )
from dalek.tools.likelihood import SSum


class SimpleTardis(Chain):

    def __init__(self, wrapper, observed_wl, observed_flux, distance=(1 * u.Mpc)):
        # Make sure we are dealing with bin edges, not centers
        assert len(observed_wl) == len(observed_flux) + 1
        super(SimpleTardis, self).__init__(
                RunInfo(),
                Prior(),
                Chain(
                    CheckPrior(),
                    Tardis(wrapper),
                    VirtualPacketProvider(),
                    VirtualLuminosity(observed_wl),
                    Flux(distance),
                    SSum(observed_wl, observed_flux),
                    breakable=True
                    ),
                Posterior(),
                )
