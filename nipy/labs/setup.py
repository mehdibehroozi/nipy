# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
from __future__ import absolute_import, print_function

import os
from distutils import log

try:  # Python 3
    from configparser import ConfigParser, NoSectionError, NoOptionError
except ImportError:  # Python 2
    from ConfigParser import ConfigParser, NoSectionError, NoOptionError

# Global variables
LIBS = os.path.realpath('lib')

# Stuff for reading setup file
SETUP_FILE = 'setup.cfg'
SECTION = 'lapack'
KEY = 'external'
EXTERNAL_LAPACK_VAR = 'NIPY_EXTERNAL_LAPACK'

def get_link_external():
    """ Return True if we should link to system BLAS / LAPACK

    If True, attempt to link to system BLAS / LAPACK.  Otherwise, compile
    lapack_lite, and link to that.

    First check ``setup.cfg`` file for section ``[lapack]`` key ``external``.

    If this value undefined, then get string from environment variable
    NIPY_EXTERNAL_LAPACK.

    If value from ``setup.cfg`` or environment variable is not 'False' or '0',
    then return True.
    """
    config = ConfigParser()
    try:
        config.read(SETUP_FILE)
        external_link = config.get(SECTION, KEY)
    except (IOError, KeyError, NoOptionError, NoSectionError):
        external_link = os.environ.get(EXTERNAL_LAPACK_VAR)
    if external_link is None:
        return False
    return external_link.lower() not in ('0', 'false')


def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration, get_numpy_include_dirs
    from numpy.distutils.system_info import get_info

    config = Configuration('labs', parent_package, top_path)

    # fff library
    config.add_include_dirs(os.path.join(LIBS,'fff'))
    config.add_include_dirs(os.path.join(LIBS,'fff_python_wrapper'))
    config.add_include_dirs(get_numpy_include_dirs())

    sources = [os.path.join(LIBS,'fff','*.c')]
    sources.append(os.path.join(LIBS,'fff_python_wrapper','*.c'))

    # Link with lapack if found on the system

    # XXX: We need to better sort out the use of get_info() for Lapack, because
    # using 'lapack' and 'lapack_opt' returns different things even comparing
    # Ubuntu 8.10 machines on 32 vs 64 bit setups.  On OSX
    # get_info('lapack_opt') does not return the keys: 'libraries' and
    # 'library_dirs', but get_info('lapack') does.
    #
    # For now this code should do the right thing on OSX and linux, but we
    # should ask on the numpy list for clarification on the proper approach.

    # XXX: If you modify these lines, remember to pass the information
    # along to the different .so in the neurospin build system.
    # First, try 'lapack_info', as that seems to provide more details on Linux
    # (both 32 and 64 bits):
    lapack_info = get_info('lapack_opt', 0)
    if 'libraries' not in lapack_info:
        # But on OSX that may not give us what we need, so try with 'lapack'
        # instead.  NOTE: scipy.linalg uses lapack_opt, not 'lapack'...
        lapack_info = get_info('lapack', 0)

    # If lapack linking not required or no lapack install is found, we
    # use the rescue lapack lite distribution included in the package
    # (sources have been translated to C using f2c)
    want_lapack_link = get_link_external()
    if not want_lapack_link:
        log.warn('Building with (slow) Lapack lite distribution: '
                 'set {0} environment variable or use setup.cfg '
                 'to enable link to optimized BLAS / LAPACK'.format(
                        EXTERNAL_LAPACK_VAR)
                 )
        sources.append(os.path.join(LIBS,'lapack_lite','*.c'))
        library_dirs = []
        libraries = []
    else: # Best-case scenario: external lapack found
        if not lapack_info:
            raise RuntimeError('Specified external lapack linking but '
                               'numpy does not report external lapack')
        log.warn('Linking with system Lapack')
        library_dirs = lapack_info['library_dirs']
        libraries = lapack_info['libraries']
        if 'include_dirs' in lapack_info:
            config.add_include_dirs(lapack_info['include_dirs'])

    # Information message
    print('LAPACK build options:')
    print('library_dirs: %s ' % library_dirs)
    print('libraries: %s ' % libraries)
    print('lapack_info: %s ' % lapack_info)

    config.add_library('cstat',
                       sources=sources,
                       library_dirs=library_dirs,
                       libraries=libraries,
                       extra_info=lapack_info)

    # Subpackages
    config.add_subpackage('bindings')
    config.add_subpackage('glm')
    config.add_subpackage('group')
    config.add_subpackage('spatial_models')
    config.add_subpackage('utils')
    config.add_subpackage('viz_tools')
    config.add_subpackage('datasets')
    config.add_subpackage('tests')

    config.make_config_py() # installs __config__.py

    return config

if __name__ == '__main__':
    print('This is the wrong setup.py file to run')
