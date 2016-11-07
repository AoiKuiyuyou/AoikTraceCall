# coding: utf-8
"""
Setup module.
"""
from __future__ import absolute_import

# External imports
from setuptools import find_packages
from setuptools import setup


setup(
    name='AoikTraceCall',

    version='0.0.2',

    description=(
        'Trace Python function calls selected by regular expressions.'
    ),

    long_description="""`Documentation on Github
<https://github.com/AoiKuiyuyou/AoikTraceCall>`_""",

    url='https://github.com/AoiKuiyuyou/AoikTraceCall',

    author='Aoi.Kuiyuyou',

    author_email='aoi.kuiyuyou@google.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='trace function call',

    package_dir={
        '': 'src'
    },

    packages=find_packages('src'),

    include_package_data=True,

    install_requires=[
        'pyfiglet>=0.7.5'
    ]
)
