import pytest
from dalek.tools.prior import Prior, CheckPrior, INVALID
from dalek.tools.base import Chain, Link


class Dummy(Link):
    outputs = ('dummy',)

    def calculate(self):
        return True

prior_pars = pytest.mark.parametrize(
        ['o', 'expected'],
        [
            (0, INVALID),
            (0.1, 0),
            ]
        )
@prior_pars
def test_prior(o, expected):
    idict = {
            'parameters': {
                'model.abundances.o': o,
                },
            }

    prior = Prior()
    obtained = prior(idict)['logprior']
    assert obtained == expected


@prior_pars
def test_checkprior(o, expected):
    idict = {
            'parameters': {
                'model.abundances.o': o,
                },
            }

    prior = Chain(Prior(), Chain(CheckPrior(), Dummy(), breakable=True))
    obtained = prior(idict)['dummy']
    expected = True if expected == 0 else None
    assert obtained == expected
