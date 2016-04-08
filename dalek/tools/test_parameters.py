import sys
import pytest
from dalek.tools.parameters import (
        Parameter, ParameterContainer,
        DynamicParameter,
        OverFlowParameter,
        )


@pytest.mark.parametrize(
        ['bounds'],
        [
            ((0,10),),
            ((10,20),),
            ]
        )
def test_dynamic_parameter(bounds):
    a = DynamicParameter('c.b.a', bounds=bounds, default=0.5)
    a.value = 0.1
    assert a.value == 1 + bounds[0]
    assert a.transform(0) == bounds[0]
    assert a.transform(1) == bounds[1]
    with pytest.raises(ValueError):
        a.value=1.1

def test_parameter_init():
    a = Parameter('c.b.a', default=0.5)
    assert a.name == 'a'
    assert a.base_path == 'c.b'
    assert a.path == 'c.b.a'
    assert a.full_name == 'c_b_a'
    assert a.value == 0.5
    b = Parameter('test')
    assert b.name == 'test'
    assert b.base_path == ''
    assert b.path == 'test'


def test_parameter_function():
    a = DynamicParameter(
            'test',
            transformation = lambda x, a, b: x/(1-x+sys.float_info.min))
    assert a.transform(0.5) == 1


def test_container():
    cont = ParameterContainer(
            DynamicParameter('a.b.c', bounds=(0, 0.4)),
            DynamicParameter('a.b.d', bounds=(0, 0.8)),
            DynamicParameter('c.b.a', bounds=(0,0.8)),
            OverFlowParameter('a.b.overflow'),
            )
    assert isinstance(cont.c_b_a, Parameter)
    assert cont.c_b_a.value == 0

    cont.values = [0.5, 0.5, 0.3]
    assert cont.values == [0.2, 0.4, 0.24, 0.4]

    with pytest.raises(ValueError):
        cont.values = [0.75, 1, 0.3]
    cont = ParameterContainer(
            OverFlowParameter('a.b.overflow'),
            DynamicParameter('a.b.c', bounds=(0, 0.2)),
            DynamicParameter('c.b.a', bounds=(0,0.8)),
            )
    cont.values = [0.5, 0.3]
    assert cont.values == [0.9, 0.1, 0.24]
