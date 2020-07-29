#!/usr/bin/env python
from __future__ import absolute_import
from setuptools import setup, find_packages


setup(
    name='django-curation',
    version="2.0.0b1",
    description='A model used for curating other models and proxying their attributes',
    author='The Atlantic',
    author_email='programmers@theatlantic.com',
    url='https://github.com/theatlantic/django-curation',
    packages=find_packages(),
    python_requires='!=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4*, <4',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
   ],
    include_package_data=True,
    zip_safe=False,
)
