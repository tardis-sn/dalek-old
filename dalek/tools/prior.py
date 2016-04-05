import numpy as np

from dalek.tools.base import Link, BreakChainException

INVALID = -np.inf
DEFAULT = 0

class Prior(Link):
    '''
    A very basic prior with the ability to break execution of a subchain.
    '''
    inputs = ('parameters',)
    outputs = ('logprior',)

    def calculate(self, parameters):
        try:
            o = parameters['model.abundances.o']
        except KeyError:
            pass
        else:
            if o <= 0.:
                return INVALID
        try:
            s = parameters['model.abundances.s']
            si = parameters['model.abundances.si']
        except KeyError:
            pass
        else:
            if s > si:
                return INVALID
        return DEFAULT


class CheckPrior(Link):
    '''
    This will break the innermost dalek.tools.base.Chain to save computing time
    if the prior is INVALID.
    This should be the first element in the Chain containing the Tardis
    evaluation.
    '''
    inputs = ('logprior',)

    def calculate(self, prior):
        if prior == INVALID:
            raise BreakChainException(
                    'Prior is INVALID: {}'.format(prior))


