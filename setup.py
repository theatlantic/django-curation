#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import curation

setup(
    name='django-curation',
    version="1.0.27",
    description='A model used for curating other models and proxying their attributes',
    author='The Atlantic',
    author_email='atmoprogrammers@theatlantic.com',
    url='https://github.com/theatlantic/django-curation',
    packages=find_packages(),
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
)
