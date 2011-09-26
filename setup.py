from setuptools import setup

setup(
    name='django-magazine',
    version='0.1.0',
    description='A Django app for managing magazine articles, issues and authors.',
    long_description=open('README.md').read(),
    author='Dominic Rodger',
    author_email='internet@dominicrodger.com',
    url='http://github.com/dominicrodger/django-magazine',
    license='BSD',
    packages=['magazine'],
    include_package_data=True,
    package_data={'': ['README.md']},
    zip_safe=False,
    install_requires=['Django', 'South', 'bleach', 'django-tinymce', 'html5lib',]
)
