import bleach
from style_stripper import strip_styles


allowed_tags = bleach.ALLOWED_TAGS + ['p', 'h1', 'h2', 'h3', 'h4', 'h5', ]
allowed_attributes = bleach.ALLOWED_ATTRIBUTES.copy()
allowed_attributes['a'] = bleach.ALLOWED_ATTRIBUTES['a'] + ['name']


def clean_word_text(text):
    text = strip_styles(text)

    text = bleach.clean(text,
                        tags=allowed_tags,
                        strip=True,
                        attributes=allowed_attributes)

    return text
