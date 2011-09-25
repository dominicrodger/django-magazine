import bleach
from lxml.html.clean import Cleaner

allowed_tags = bleach.ALLOWED_TAGS + ['p', 'h1', 'h2', 'h3', 'h4', 'h5',]
allowed_attributes = bleach.ALLOWED_ATTRIBUTES.copy()
allowed_attributes['a'] = bleach.ALLOWED_ATTRIBUTES['a'] + ['name']

def clean_word_text(text):
    # The only thing I need Cleaner for is to clear out the contents of
    # <style>...</style> tags
    cleaner = Cleaner(style = True)
    text = cleaner.clean_html(text)

    text = bleach.clean(text, tags = allowed_tags, strip = True, attributes = allowed_attributes)

    return text