from django import template
from django.template.loader import render_to_string
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