import bleach

allowed_tags = bleach.ALLOWED_TAGS + ['p', 'h1', 'h2',]
allowed_attributes = bleach.ALLOWED_ATTRIBUTES.copy()
allowed_attributes['a'] = bleach.ALLOWED_ATTRIBUTES['a'] + ['name']

def clean_word_text(text):
    text = bleach.clean(text, tags = allowed_tags, strip = True, attributes = allowed_attributes)

    return text