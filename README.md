# django-magazine

A pluggable Django app for managing a simple magazine.

Magazines consist of Issues, each of which contains one or more
Articles, which are by one or more Authors.

## Getting Started

It's not currently on PyPI (though will be soon), so for now you have
to install with:

    pip install git+ssh://git@github.com/dominicrodger/django-magazine.git

Presuming you already have a Django project set up, add `magazine` to
your `INSTALLED_APPS` setting, and add:

    url(r'^', include('magazine.urls')),

to your `urls.py`.

## Tests

django-magazine is tested with every push. Our current build status is
[![Build Status](https://secure.travis-ci.org/dominicrodger/django-magazine.png?branch=master)](http://travis-ci.org/dominicrodger/django-magazine).

Once you've added `magazine` to your `INSTALLED_APPS`, you can run its
tests with:

    manage.py test magazine

## Dependencies

django-magazine requires at least Python 2.6, since it uses the newer
[string formatting syntax][format]. If you need to use Python 2.5,
feel free to submit a pull request that fixes that.

This app depends on [Bleach](https://github.com/jsocol/bleach), for
cleaning up submitted HTML (particularly content pasted in from
Microsoft Word).

This app requires at least [Django 1.3.1][django1.3], since it depends
on the new [`{% with %}`][with-tag] tag behaviour, and the new
[`{% include %}`][include-tag] behaviour.

This app uses [South](http://south.aeracode.org/) for managing
database changes, though you don't have to.

[django1.3]: https://docs.djangoproject.com/en/dev/releases/1.3/
[with-tag]: https://docs.djangoproject.com/en/1.3/ref/templates/builtins/#with
[include-tag]: https://docs.djangoproject.com/en/1.3/ref/templates/builtins/#include
[format]: http://docs.python.org/whatsnew/2.6.html#pep-3101-advanced-string-formatting "Read about the new string formatting functionality in Python 3.0, backported to Python 2.6"
