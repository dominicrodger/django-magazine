from django.test import TestCase
from magazine.utils.word_cleaner import clean_word_text


class HTMLSanitizerTestCase(TestCase):
    def testStripAttributes(self):
        html = (u"<a href=\"foobar\" name=\"hello\""
                u"title=\"View foobar\" onclick=\"malicious()\">hello!</a>")

        self.assertEqual(clean_word_text(html),
                         u"<a href=\"foobar\" name=\"hello\" "
                         "title=\"View foobar\">"
                         "hello!</a>")

    def testStripTags(self):
        html = u'<script type="text/javascript">alert("what?");</script>hello!'
        self.assertEqual(clean_word_text(html), u'alert("what?");hello!')

    def testStyleStripped(self):
        html = u'<style>foobar</style><p>hello!</p>'
        self.assertEqual(clean_word_text(html), u'<p>hello!</p>')

        # Check we're not reliant on the <style> tag looking a
        # particular way
        html = u"""
<style type="text/css" somethingelse="something">foobard</style>
<p>hello!</p>
"""
        self.assertEqual(clean_word_text(html), u'<p>hello!</p>')

        # Check we don't care about case
        html = u"""
<STYLE TYPE="TEXT/CSS" somethingelse="something">foobar</STYLE>
<p>hello!</p>
"""
        self.assertEqual(clean_word_text(html), u'<p>hello!</p>')

        # Check multiple style blocks are stripped
        html = u"""
<STYLE TYPE="TEXT/CSS" somethingelse="something">foobar</STYLE>
<p>hello!</p>
<style type="text/css" somethingelse="something">foobar</style>
"""
        self.assertEqual(clean_word_text(html), u'<p>hello!</p>')

    def testStyleStrippedEmptyTag(self):
        # Check we don't do much other than strip the style tag
        # for empty style tags
        html = u"""
<style type="text/css" somethingelse="something" /><p>hello!</p>"""
        self.assertEqual(clean_word_text(html), u'<p>hello!</p>')

    def testEmpty(self):
        html = u''
        self.assertEqual(clean_word_text(html), u'')
