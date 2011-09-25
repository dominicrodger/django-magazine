from django import template
from django.template.defaultfilters import stringfilter
from django.template.loader import render_to_string
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def magazine_authors(authors):
    if not authors:
        return ''

    authors = list(authors)

    if len(authors) == 1:
        return render_to_string('magazine/_individual_author.html', {'author': authors[0]})
    else:
        first_bit = ', '.join([ render_to_string('magazine/_individual_author.html', {'author': author}) for author in authors[0:-1]])
        second_bit = ' and ' + render_to_string('magazine/_individual_author.html', {'author': authors[-1]})
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

    return mark_safe(value)
ampersands.needs_autoescape = True