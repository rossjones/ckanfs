from distutils.core import setup
import setuptools

setup(
    name='CKANfs',
    version='0.1',
    packages=['ckanfs',],
    long_description=open('README.md').read(),
    install_requires=[
      'fusepy>=3.0',
      'ckanapi>=4.3'
    ],
    scripts=['bin/ckanfs'],
)