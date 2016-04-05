import pytest
import logging

from tardis import run_tardis
logging.getLogger('tardis').setLevel(logging.ERROR)




@pytest.fixture(scope='module')
def config_path():
    return "/home/stefan/projects/dalek/data/wrapper-test/quick_test.yml"


@pytest.fixture(scope='module')
def log_path():
    return "/home/stefan/projects/dalek/data/wrapper-test/test/logs/"



@pytest.fixture(scope='module')
def model(config_path):
    return run_tardis(config_path)
