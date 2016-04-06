class Parameter(object):

    def __init__(self, path, bounds=(0,1), default=0,
            transformation=lambda x, a, b : a + x * (b-a)):
        self._bounds = bounds
        self._transform = transformation
        self.path = path
        self.value = default

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new):
        self._value = self.transform(new)

    def transform(self, x):
        if x>1 or x<0:
            raise ValueError(
            'Parameter.transform: expected input is [0,1]. Received: {}'
            .format(x))
        else:
            return self._transform(x, self._bounds[0], self._bounds[1])

    @property
    def name(self):
        return self.path.split('.')[-1]

    @property
    def base_path(self):
        return '.'.join(self.path.split('.')[:-1])


class CalculatedParameter(Parameter):
# This is kind of hacky, sorry
    pass


class OverFlowParameter(CalculatedParameter):

    def __init__(self, path, bounds=(0,1)):
        self._bounds = bounds
        self.path = path
        self._value = bounds[0]

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, container):
        parameters = container._parameters
        value = self._bounds[1]
        for p in parameters:
            if p.base_path == self.base_path:
                value -= p.value
        if value > self._bounds[0] and value < self._bounds[1]:
            self._value = value
        else:
            raise ValueError(
                    'OverFlowParameter is out of bounds: {} is outside of {}'
                    .format(value, self._bounds))


class ParameterContainer(object):
    n_pars=0

    def __init__(self, *args, **kwargs):
        self._parameters = []
        for arg in args:
            if isinstance(arg, Parameter):
                setattr(self, arg.name, arg)
                self.n_pars += 1
                self._parameters.append(arg)

    def __iter__(self):
        for p in self._parameters:
            yield p.path, p.value

    @property
    def values(self):
        return [ p.value for p in self._parameters]

    @values.setter
    def values(self, new):
        calc_pars = list()
        for p in self._parameters:
            try:
                p.value = new[0]
            except AttributeError:
                # Seems like a CalcParameter
                calc_pars.append(p)
            except IndexError as e:
                if p == self._parameters[-1]:
                    calc_pars.append(p)
                else:
                    raise e
            else:
                new.pop(0)
        for p in calc_pars:
            p.value = self
