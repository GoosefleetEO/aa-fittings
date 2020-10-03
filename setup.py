# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

from fittings import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = [
    'allianceauth>=2.7.3',
    'django-bootstrap-form',
    'django-model_utils>=3.1.1',
    'django-esi>=2.0.0'
]

testing_extras = [

]

setup(
    name='fittings',
    version=__version__,
    author='Col Crunch',
    author_email='it-team@serin.space',
    description='A simple fittings and doctrine management application.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=install_requires,
    extras_require={
        'testing': testing_extras,
        ':python_version=="3.6"': ['typing'],
    },
    python_requires='~=3.6',
    license='GPLv3',
    packages=find_packages(),
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.1',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    url='https://gitlab.com/colcrunch/fittings',
    zip_safe=False,
    include_package_data=True,
)