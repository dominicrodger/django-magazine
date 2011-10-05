from setuptools import setup, find_packages

import magazine

setup(
    name='django-magazine',
    version=magazine.__version__,
    description='A Django app for managing magazine articles, issues and authors.',
    long_description=open('README.md').read(),
    author='Dominic Rodger',
    author_email='internet@dominicrodger.com',
    url='http://github.com/dominicrodger/django-magazine',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
)
