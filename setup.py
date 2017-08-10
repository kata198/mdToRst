#!/usr/bin/env python
# vim: set ts=4 sw=4 st=4 expandtab 
'''
    mdToRst - Convert markdown (md) to restructed text (rst)

    Copyright (c) 2017 Timothy Savannah, All Rights Reserved

    Licensed under terms of the GNU General Public License (GPL) Version 3.0

    You should have recieved a copy of this license as "LICENSE" with the source distribution,
      otherwise the current license can be found at https://github.com/kata198/mdToRst/blob/master/LICENSE


    mdToRst - Main executable to perform the actions provided by the md_to_rst module
'''


#vim: set ts=4 sw=4 expandtab

import os
import sys
from setuptools import setup


if __name__ == '__main__':
 

    dirName = os.path.dirname(__file__)
    if dirName and os.getcwd() != dirName:
        os.chdir(dirName)

    summary = 'Tool and library to convert markdown to restructed text (md to rst)'

    try:
        with open('README.rst', 'rt') as f:
            long_description = f.read()
    except Exception as e:
        sys.stderr.write('Exception when reading long description: %s\n' %(str(e),))
        long_description = summary

    setup(name='mdToRst',
            version='1.1.0',
            packages=['md_to_rst'],
            scripts=['mdToRst'],
            author='Tim Savannah',
            author_email='kata198@gmail.com',
            maintainer='Tim Savannah',
            url='https://github.com/kata198/mdToRst',
            maintainer_email='kata198@gmail.com',
            description=summary,
            long_description=long_description,
            license='LGPLv3',
            keywords=['markdown', 'md', 'restructed', 'text', 'rst', 'convert', 'mdToRst', 'documentation', 'readme', 'README.md', 'README.rst'],
            classifiers=['Development Status :: 4 - Beta',
                         'Programming Language :: Python',
                         'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                         'Programming Language :: Python :: 2',
                          'Programming Language :: Python :: 2',
                          'Programming Language :: Python :: 2.7',
                          'Programming Language :: Python :: 3',
                          'Programming Language :: Python :: 3.3',
                          'Programming Language :: Python :: 3.4',
                          'Programming Language :: Python :: 3.5',
                          'Programming Language :: Python :: 3.6',
                          'Intended Audience :: Developers',
                          'Topic :: Documentation',
                          'Topic :: Software Development :: Documentation',
                          'Topic :: Text Processing',
                          'Topic :: Text Processing :: Markup',
                          'Topic :: Utilities',
                          'Topic :: Software Development :: Libraries :: Python Modules',
            ]
    )

