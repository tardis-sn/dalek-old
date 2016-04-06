import sys
import pytest
from dalek.tools.parameters import (
        Parameter, ParameterContainer,
        OverFlowParameter,
        )


@pytest.mark.parametrize(
        ['bounds'],
        [
            ((0,10),),
            ((10,20),),
            ]
        )
def test_parameter(bounds):
    a = Parameter('c.b.a', bounds=bounds, default=0.5)
    assert a.name == 'a'
    assert a.base_path == 'c.b'
    assert a.value == 5 + bounds[0]
    a.value = 0.1
    assert a.value == 1 + bounds[0]
    assert a.transform(0) == bounds[0]
    assert a.transform(1) == bounds[1]
    with pytest.raises(ValueError):
        a.value=1.1

    b = Parameter('test')
    assert b.name == 'test'
    assert b.base_path == ''
    assert b.path == 'test'


def test_parameter_function():
    a = Parameter('test', transformation = lambda x, a, b: x/(1-x+sys.float_info.min))
    assert a.transform(0.5) == 1


def test_container():
    cont = ParameterContainer(
            Parameter('a.b.c', bounds=(0, 0.2)),
            Parameter('c.b.a', bounds=(0,0.8)),
            OverFlowParameter('a.b.overflow'),
            )
    def overflow(x,a,b):
        return 1 - cont.a.value - cont.b.value
    assert isinstance(cont.a, Parameter)
    assert cont.a.value == 0

    cont.values = [0.5, 0.3]
    cont = ParameterContainer(
            OverFlowParameter('a.b.overflow'),
            Parameter('a.b.c', bounds=(0, 0.2)),
            Parameter('c.b.a', bounds=(0,0.8)),
            )
    cont.values = [0.5, 0.3]

