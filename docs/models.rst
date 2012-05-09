Models
======

.. note::
    django-magazine also has another model which the documentation
    does not refer to, since it will be removed soon -
    BookReview. This model was relevant to one particular use case of
    django-magazine, but is unlikely to be useful to most people.


There are 3 main models in django-magazine: Issue, Article and
Author. An Issue is made up of Articles, each of which by at least one
Author.

Issue
-----

Issues have three main properties: number, date, and whether or not it
is published.

:Issue Number: These are intended to be used as sequential issue
               numbers, and must be unique.

:Date: This is the publication date of the issue - note that an issue
       is only considered published if this is on or before the
       current date, and the published flag is ``True``.

:Published: Used for creating draft issues - you can safely mark an
            issue with a date in the future as published - it will
            only be publically accessible once the publication date is
            reached.

Embargoing Issues
^^^^^^^^^^^^^^^^^

Sometimes it's useful to just show teasers of content - perhaps for
very recent content, or for old content, perhaps to encourage users to
subscribe to a dead-tree version. At present, this functionality isn't
very fleshed out (it just shows teaser content to everyone other than
site staff), in future, I'm hoping this will take into account the
current user, to allow showing full content if you're logged in, for
example.

There are two settings relevant to this feature:

:MAGAZINE_IS_EMBARGOED_FUNCTION: Set to a function which takes an
                                 ``Issue`` object and returns ``True``
                                 if that issue is embargoed.

:MAGAZINE_EMBARGO_TIME_IN_MONTHS: If
                                  ``MAGAZINE_IS_EMBARGOED_FUNCTION``
                                  is not set, then this will determine
                                  how many months old an issue has to
                                  be before it is no longer embargoed.

If an issue is embargoed, a teaser will be shown. The teaser is either
the article's description, or the first 50 words of the article.

Article
-------

Articles are the content of magazines. Each article belongs to an
issue, and is by one or more authors.

Articles are ordered within an issue, based on the value of
``order_in_issue`` (articles with lower values are shown first).

.. note::
    Article text will be cleaned up automatically with bleach_, which
    strips out bad HTML that tends to be added by programs like
    Microsoft Word. The only allowed tags are those set by
    ``bleach.ALLOWED_TAGS``, ``<p>``, and ``<h[1-5]>``.

.. _bleach: https://github.com/jsocol/bleach

Author
------

Authors have names, and a quick biography.

Sometimes, you don't want users to be able to see a list of articles
by a particular author (e.g. when importing articles where the author
is unknown, you might want to attribute the article to "Unknown", so
that something shows up where the list of authors would normally
be). To do this, just uncheck the ``indexable`` value of the author.

