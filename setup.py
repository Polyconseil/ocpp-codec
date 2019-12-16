
# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

readme = ''

setup(
    long_description=readme,
    name='ocpp-codec',
    version='0.1.0',
    description='OCPP 1.6 and 2.0 messages encoder in Python',
    python_requires='==3.*,>=3.7.0',
    author='Polyconseil',
    license='BSD-3-Clause',
    packages=['ocpp_codec', 'ocpp_codec.v16', 'ocpp_codec.v20'],
    package_dir={"": "."},
    package_data={},
    install_requires=['python-dateutil==2.*,>=2.8.0', 'pytz==2019.*,>=2019.3.0'],
    extras_require={"dev": ["pytest==5.*,>=5.3.0", "pytest-mock==1.*,>=1.13.0"]},
)
