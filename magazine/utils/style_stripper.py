import html5lib
from html5lib.constants import tokenTypes
from html5lib.sanitizer import HTMLSanitizerMixin
from html5lib.serializer.htmlserializer import HTMLSerializer
from html5lib.tokenizer import HTMLTokenizer


class StyleSanitizerMixin(HTMLSanitizerMixin):
    def sanitize_token(self, token):
        if not hasattr(self, 'in_style_tag'):
            self.in_style_tag = False

        # If we're in a style tag - mark our position as such, and
        # discard the token.
        if token.get('name') == 'style':
            if token['type'] == tokenTypes['StartTag']:
                if not token['selfClosing']:
                    self.in_style_tag = True
                return
            if token['type'] == tokenTypes['EndTag']:
                self.in_style_tag = False
                return

        if self.in_style_tag:
            # We're in a style tag, so we want to discard this token
            return

        # We're not in a style tag, so we want to keep this token
        return token


class StyleSanitizer(HTMLTokenizer, StyleSanitizerMixin):
    def __iter__(self):
        for token in HTMLTokenizer.__iter__(self):
            token = self.sanitize_token(token)
            if token:
                yield token


def strip_styles(text):
    parser = html5lib.HTMLParser(tokenizer=StyleSanitizer)
    domtree = parser.parseFragment(text)
    walker = html5lib.treewalkers.getTreeWalker('simpletree')
    stream = walker(domtree)
    try:
        serializer = HTMLSerializer(quote_attr_values=True,
                                    omit_optional_tags=False)
        return serializer.render(stream)
    except AssertionError:
        return domtree.toxml()
