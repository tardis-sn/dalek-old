class Parameter(object):
    """
    A static Parameter whose value can't be changed.

    Make sure to change the default value of 0.0 during initialization.
    """

    def __init__(self, path, default=0.0):
        self.path = path
        self._value = default

    @property
    def value(self):
        return self._value

    @property
    def name(self):
        return self.path.split('.')[-1]

    @property
    def base_path(self):
        return '.'.join(self.path.split('.')[:-1])

    @property
    def full_name(self):
        return '_'.join(self.path.split('.'))



class DynamicParameter(Parameter):
    """
    A Parameter whose value can be updated and transformed with a function.

    Keyword arguments:
    bounds -- Tuple of lower and upper bounds of the result (default: (0,1) )
    transformation -- function f(x, bounds[0], bounds[1]) mapping [0,1]
                        onto the bounds interval (default: linear map)
    """

    def __init__(self, *args, **kwargs):
        self._ftransform = kwargs.pop('transformation', lambda x, a, b : a + x * (b-a))
        self._bounds = kwargs.pop('bounds', (0,1))
        super(DynamicParameter, self).__init__(*args, **kwargs)

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
            return self._ftransform(x, self._bounds[0], self._bounds[1])


class DependentParameter(Parameter):
    """
    A Parameter that depends on the value of other parameters.

    It's value gets updated after other parameters.
    Currently two parameters depending on each other results in unexpected
    behavior and should be avoided.
    Subclasses should define an update(self, parameters) function to return
    the new value.

    Keyword arguments:
    bounds -- Tuple of lower and upper bounds of the result (default: (0,1) )
    """


    def __init__(self, *args, **kwargs):
        self._bounds = kwargs.pop('bounds', (0,1))
        match = kwargs.pop('match', None)
        super(DependentParameter, self).__init__(*args, **kwargs)
        self._match_string = match or self.base_path

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, container):
        parameters = container._parameters
        self._value = self.update(parameters)


class OverFlowParameter(DependentParameter):

    def update(self, parameters):
        value = self._bounds[1]
        for p in parameters:
            if p.base_path == self._match_string:
                value -= p.value
        if value > self._bounds[0] and value < self._bounds[1]:
            return value
        else:
            raise ValueError(
                    'OverFlowParameter is out of bounds: {} is outside of {}'
                    .format(value, self._bounds))


class ParameterContainer(object):
    n_pars=0

    def __init__(self, *args, **kwargs):
        self._parameters = []
        self._input_pars = []
        self._dep_pars = []
        for arg in args:
            if isinstance(arg, Parameter):
                setattr(self, arg.full_name, arg)
                self.n_pars += 1
                self._parameters.append(arg)
                if isinstance(arg, DynamicParameter):
                    self._input_pars.append(arg)
                elif isinstance(arg, DependentParameter):
                    self._dep_pars.append(arg)

    @property
    def values(self):
        return [ p.value for p in self._parameters]

    @values.setter
    def values(self, new):
        assert len(new) == len(self._input_pars)
        for p, v in zip(self._input_pars, new):
            p.value = v
        for p in self._dep_pars:
            p.value = self

    def __iter__(self):
        for p in self._parameters:
            yield p.path, p.value

    def __getitem__(self, name):
        for p in self._parameters:
            if p.path == name:
                return p.value

    def items(self):
        for p in self._parameters:
            yield p.path, p.value

    @property
    def dict(self):
        return {p.path: p.value for p in self._parameters}
