from django import template
from django.core.cache import cache
from django.template.defaultfilters import stringfilter
from django.template.loader import render_to_string
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()


def __get_cached_authors_key(object):
    return u'magazine_authors_{0}_{1}'.format(object.__class__.__name__,
                                              object.pk),


def __get_cached_authors(object):
    key = __get_cached_authors_key(object)

    authors = cache.get(key)

    if not authors:
        authors = object.all_authors()
        if authors:
            cache.set(key, authors, 3600)

    return authors


@register.simple_tag
def magazine_authors(object):
    authors = __get_cached_authors(object)
    if not authors:
        return ''

    authors = list(authors)

    if len(authors) == 1:
        return render_to_string('magazine/_individual_author.html',
                                {'author': authors[0]})
    else:
        final_author = render_to_string('magazine/_individual_author.html',
                                        {'author': authors[-1]})
        first_bit = ', '.join(
            [render_to_string('magazine/_individual_author.html',
                              {'author': author}) for author in authors[0:-1]])
        second_bit = ' and ' + final_author
        result = first_bit + second_bit
    return mark_safe(result)


@register.filter
@stringfilter
def ampersands(value, autoescape=None):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x

    value = esc(value)

    pretty_ampersand = u' <span class="ampersand">&amp;</span> '

    value = value.replace(' and ', pretty_ampersand)
    value = value.replace(' &amp; ', pretty_ampersand)

    if not autoescape:
        value = value.replace(' & ', pretty_ampersand)

    return mark_safe(value)
ampersands.needs_autoescape = True
