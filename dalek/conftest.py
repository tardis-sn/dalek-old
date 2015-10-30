# this contains imports plugins that configure py.test for astropy tests.
# by importing them here in conftest.py they are discoverable by py.test
# no matter how it is invoked within the source tree.

from astropy.tests.pytest_plugins import *

from astropy.utils.argparse import writeable_directory

#from astropy.tests.pytest_plugins import pytest_addoption as addoption_ap

## Uncomment the following line to treat all DeprecationWarnings as
## exceptions
# enable_deprecations_as_exceptions()

## Uncomment and customize the following lines to add/remove entries
## from the list of packages for which version numbers are displayed
## when running the tests
# try:
#     PYTEST_HEADER_MODULES['Astropy'] = 'astropy'
#     PYTEST_HEADER_MODULES['scikit-image'] = 'skimage'
#     del PYTEST_HEADER_MODULES['h5py']
# except NameError:  # needed to support Astropy < 1.0
#     pass

## Uncomment the following lines to display the version number of the
## package rather than the version number of Astropy in the top line when
## running the tests.
# import os
#
## This is to figure out the affiliated package version, rather than
## using Astropy's
# from . import version
#
# try:
#     packagename = os.path.basename(os.path.dirname(__file__))
#     TESTED_VERSIONS[packagename] = version.version
# except NameError:   # Needed to support Astropy <= 1.0.0
#     pass

def pytest_addoption(parser):
    parser.addoption("--remote-data", action="store_true",
                     help="run tests with online data")
    parser.addoption("--open-files", action="store_true",
                     help="fail if any test leaves files open")

    parser.addoption("--doctest-plus", action="store_true",
                     help="enable running doctests with additional "
                     "features not found in the normal doctest "
                     "plugin")

    parser.addoption("--doctest-rst", action="store_true",
                     help="enable running doctests in .rst documentation")

    parser.addoption("--config-dir", nargs='?', type=writeable_directory,
                     help="specify directory for storing and retrieving the "
                          "Astropy configuration during tests (default is "
                          "to use a temporary directory created by the test "
                          "runner); be aware that using an Astropy config "
                          "file other than the default can cause some tests "
                          "to fail unexpectedly")

    parser.addoption("--cache-dir", nargs='?', type=writeable_directory,
                     help="specify directory for storing and retrieving the "
                          "Astropy cache during tests (default is "
                          "to use a temporary directory created by the test "
                          "runner)")

    parser.addini("doctest_plus", "enable running doctests with additional "
                  "features not found in the normal doctest plugin")

    parser.addini("doctest_norecursedirs",
                  "like the norecursedirs option but applies only to doctest "
                  "collection", type="args", default=())

    parser.addini("doctest_rst",
                  "Run the doctests in the rst documentation",
                  default=False)

    parser.addini("config_dir",
                  "specify directory for storing and retrieving the "
                  "Astropy configuration during tests (default is "
                  "to use a temporary directory created by the test "
                  "runner); be aware that using an Astropy config "
                  "file other than the default can cause some tests "
                  "to fail unexpectedly", default=None)

    parser.addini("cache_dir",
                  "specify directory for storing and retrieving the "
                  "Astropy cache during tests (default is "
                  "to use a temporary directory created by the test "
                  "runner)", default=None)

    parser.addini("open_files_ignore",
                  "when used with the --open-files option, allows "
                  "specifying names of files that may be ignored when "
                  "left open between tests--files in this list are matched "
                  "may be specified by their base name (ignoring their full "
                  "path) or by absolute path", type="args", default=())

    parser.addoption('--repeat', action='store',
                     help='Number of times to repeat each test')



import dalek
import os

@pytest.fixture
def data_path():
    return os.path.join(dalek.__path__[0], 'data')
