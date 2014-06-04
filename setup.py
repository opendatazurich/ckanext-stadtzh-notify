from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(
    name='ckanext-stadtzh-notify',
    version=version,
    description="CKAN notifications extension for the City of Zurich",
    long_description="""\
    """,
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Liip AG',
    author_email='ogd@liip.ch',
    url='http://www.liip.ch',
    license='GPL',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.stadtzhnotify'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points=\
    """
    [ckan.plugins]
    stadtzhnotify=ckanext.stadtzhnotify.plugins:StadtzhNotify
    [paste.paster_command]
    stadtzh=ckanext.stadtzhnotify.commands.stadtzh:StadtzhCommand
    """,
)
