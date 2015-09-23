#!/usr/bin/env python

import sys

from setuptools.command.sdist import sdist

from wagtail_jinja2 import __version__

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


# Hack to prevent "TypeError: 'NoneType' object is not callable" error
# in multiprocessing/util.py _exit_function when setup.py exits
# (see http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)
try:
    import multiprocessing
except ImportError:
    pass


install_requires = [
    "Jinja2>=2.8",
    "wagtail>=1.1"
]


setup(
    name='wagtail-jinja2',
    version=__version__,
    description='Jinja2 extensions to support the main django tags on wagtail.',
    author='Arthur Rio',
    author_email='arthur@minervaproject.com',
    url='https://github.com/minervaproject/wagtail-jinja2',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    long_description=open('README.md').read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Framework :: Django',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=install_requires,
    zip_safe=False,
)

