Installation
============

.. note::
    django-magazine is not yet available on PyPI - there's some
    cleanup I need to do before I can make it available there.

Before you start
----------------

You'll need Python_ and virtualenv_ if you don't already have
them. Using a virtual environment will make the installation easier,
and will help to avoid clutter in your system-wide libraries. You will
also need Git_ to clone the repository.

.. _Python: http://www.python.org/
.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _Git: http://git-scm.com/

Trying it out
-------------

django-magazine ships with an example project so you can see what it
does quickly. Installation is as follows::

    git clone http://github.com/dominicrodger/django-magazine.git
    cd django-magazine
    virtualenv magazine
    source magazine/bin/activate
    pip install -r requirements.txt
    pip install Django
    cd magazine/example_project
    python manage.py syncdb --noinput
    python manage.py loaddata sample_magazine_data.json
    python manage.py test magazine
    python manage.py runserver

This'll add a superuser with the username ``admin`` and the password
``admin``, so you can play around with the admin site, which will be
at http://127.0.0.1:8000/admin/. It'll also create a sample issue with
a couple of articles.

Installing django-magazine
--------------------------

django-magazine is not yet available on PyPI, but in the mean time you
can install from GitHub_ like this::

    pip install git+git://github.com/dominicrodger/django-magazine.git

Then add ``magazine`` to your ``INSTALLED_APPS`` setting, and update
your database using ``syncdb`` or ``migrate`` (if you're using
South_).

.. _GitHub: https://github.com/dominicrodger/django-magazine
.. _South: http://south.aeracode.org
