from dalek.tools.base import Link


class Posterior(Link):
    inputs = ('logprior', 'loglikelihood',)
    outputs = ('posterior',)

    def calculate(self, prior, likelihood):
        try:
            return prior + likelihood
        except TypeError as e:
            if likelihood is None:
                return prior
            else:
                raise e
