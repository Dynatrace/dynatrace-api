#!/usr/bin/env python3
from setuptools import setup, find_packages
import os


def read(filename):
    return open(filename).read()


def parse_requirements(filename):
    lines = (line.strip() for line in open(filename))
    return [line for line in lines if line and not line.startswith("#")]


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
reqs_filename = os.path.join(BASE_DIR, 'requirements.txt')
readme_filename = os.path.join(BASE_DIR, 'README.md')

setup(
    name="dynatrace-syntester",
    version="0.1.1",
    author="Dynatrace",
    author_email="pawel.nalezyty@dynatrace.com",
    description="Example tester that reports results to Dynatrace external synthetic api",
    license="Apache License 2.0",
    keywords="dynatrace",
    install_requires=parse_requirements(reqs_filename),
    url="https://www.dynatrace.com/",
    packages=find_packages(),
    include_package_data=True,
    package_data={'templates': ['*'], 'data': ['*']},
    long_description=read(readme_filename),
    scripts=['synthetic-external-tester'],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3"
    ],
)
