from __future__ import absolute_import
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
import numpy as np
import os

def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration('statistics', parent_package, top_path)
    config.add_subpackage('models')
    config.add_subpackage('formula')
    config.add_subpackage('bench')
    config.add_subpackage('tests')
    config.add_include_dirs(config.name.replace('.', os.sep))
    config.add_extension('intvol', 'intvol.pyx',
                         include_dirs=[np.get_include()])
    config.add_extension('histogram', 'histogram.pyx',
                         include_dirs=[np.get_include()])
    config.add_extension('_quantile',
                         sources=['_quantile.pyx', 'quantile.c'])
    return config


if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
