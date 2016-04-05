import numpy as np
import pytest
from dalek.tools.base import Link, Chain, BreakChainException


class AppleTrue(Link):
    outputs = ['apple']
    def calculate(self):
        return True


class AppleToggle(Link):
    inputs = ['apple']
    outputs = ['apple']
    def calculate(self, apple):
        return not apple


class BananaTrue(Link):
    outputs = ['banana']
    def calculate(self):
        return True


class BananaToggle(Link):
    inputs = ['banana']
    outputs = ['banana']
    def calculate(self, banana):
        return not banana


class CherryAnd(Link):
    inputs = ['apple', 'banana']
    outputs = ['cherry']
    def calculate(self, apple, banana):
        return apple and banana


class AppleBreak(Link):
    inputs = ['apple']
    outputs = ['apple']
    def calculate(self, apple):
        if apple:
            raise BreakChainException
        else:
            return False

class ApplePie(Link):
    outputs = ['apple', 'pie']

    def calculate(self):
        return (
                True,
                False
                )


class NumpyReturn(Link):
    outputs = ('array',)

    def calculate(self):
        return np.arange(10)


@pytest.fixture
def apple():
    return AppleTrue()


@pytest.fixture
def apple_t():
    return AppleToggle()


@pytest.fixture
def banana():
    return BananaTrue()


@pytest.fixture
def banana_t():
    return BananaToggle()


@pytest.fixture
def cherry_a():
    return CherryAnd()

def test_chainable(apple, apple_t):
    assert apple({}) == apple()
    assert apple._isvalid({})
    assert not apple_t._isvalid({})


def test_apple_true(apple):
    assert apple({}) == {'apple': True}

def test_apple_toggle(apple_t):
    result = apple_t({'apple': False})
    assert  result == {'apple': True}
    with pytest.raises(ValueError):
        apple_t({})

def test_multi_chain(apple, banana):
    assert Chain(apple)({}) == apple({})
    chain = Chain(apple, banana)
    assert chain() == {'apple':True, 'banana':True}

def test_chain(apple, apple_t, banana, banana_t, cherry_a):
    input_dict = {
        'apple': False,
        'banana': True
        }
    chain = Chain(apple_t, cherry_a, banana_t)
    result = chain(input_dict)
    assert result == {
        'banana': False,
        'apple': True,
        'cherry': True,
        }
    assert Chain(chain, cherry_a)(input_dict) == {
        'banana': False,
        'apple': True,
        'cherry': False,
        }
    with pytest.raises(ValueError):
        chain({})
        chain({'banana':False})
        chain({'apple':False})

def test_chain_init(apple, banana, cherry_a):
    chain = Chain(apple, banana, cherry_a)
    assert chain.inputs == set()
    assert chain.outputs == set(['apple', 'banana', 'cherry'])
    assert Chain(apple, cherry_a).inputs == set(['banana'])
    assert Chain(apple, cherry_a).outputs  == set(['apple', 'banana', 'cherry'])

def test_breakable_chain(apple, apple_t, banana, banana_t):
    cond = AppleBreak()
    Chain(apple, apple_t, cond, banana)()
    with pytest.raises(BreakChainException):
        Chain(apple, banana, cond, banana_t)()
    assert Chain(apple, banana, cond, banana_t, breakable=True)() == {
            'apple': True,
            'banana': True
            }
    assert Chain(apple, banana, apple_t, cond, banana_t, breakable=True)() == {
            'apple': False,
            'banana': False
            }

    assert Chain(apple, cond, banana, breakable=True)() == {
            'apple': True,
            'banana': None
            }

def test_applepie():
    ap = ApplePie()
    assert ap() == {
            'apple': True,
            'pie': False
            }

def test_numpy():
    nparray = NumpyReturn()
    assert np.all(nparray()['array'] == np.arange(10))
