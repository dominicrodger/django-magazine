from django.core.urlresolvers import reverse
from django.test import TestCase
from django.template.defaultfilters import striptags
from django.template.loader import render_to_string
from magazine.models import Author


class AuthorTestCase(TestCase):
    fixtures = ['test_authors.json', ]

    def setUp(self):
        self.paul = Author.objects.get(pk=1)
        self.dom = Author.objects.get(pk=2)
        self.bugs = Author.objects.get(pk=3)

    def testUnicode(self):
        self.assertEqual(self.paul.__unicode__(), u'Paul Beasley-Murray')
        self.assertEqual(self.dom.__unicode__(), u'Dominic Rodger')

    def testSurnameForename(self):
        self.assertEqual(self.paul.surname_forename(), u'Beasley-Murray, Paul')
        self.assertEqual(self.dom.surname_forename(), u'Rodger, Dominic')
        self.assertEqual(self.bugs.surname_forename(), u'Bugs')

    def testGetURL(self):
        self.assertEqual(self.paul.get_absolute_url(),
                         reverse('magazine_author_detail',
                                 args=[self.paul.pk, ]))
        self.assertEqual(self.dom.get_absolute_url(),
                         reverse('magazine_author_detail',
                                 args=[self.dom.pk, ]))

    def testAuthorTemplate(self):
        class AuthorHolder(object):

            def __init__(self, pk, authors):
                self.pk = pk
                self.authors = authors

            def all_authors(self):
                return self.authors

        result = (render_to_string('magazine/_authors.html',
                                   {'object': AuthorHolder(1, [])}))
        self.assertEqual(result.strip(), '')

        result = (render_to_string('magazine/_authors.html',
                                   {'object': AuthorHolder(2, [self.paul, ])}))
        self.assertEqual(striptags(result).strip(), 'Paul Beasley-Murray')
        self.assertNotEqual(result.find(self.paul.get_absolute_url()), -1)
        self.assertEqual(result.find(self.dom.get_absolute_url()), -1)
        self.assertEqual(result.find(reverse('magazine_author_detail',
                                             args=[self.bugs.pk, ])), -1)

        paul_and_dom = AuthorHolder(3, [self.paul, self.dom, ])
        result = render_to_string('magazine/_authors.html',
                                  {'object': paul_and_dom})
        self.assertEqual(striptags(result).strip(),
                         'Paul Beasley-Murray and Dominic Rodger')
        self.assertNotEqual(result.find(self.paul.get_absolute_url()), -1)
        self.assertNotEqual(result.find(self.dom.get_absolute_url()), -1)
        self.assertEqual(result.find(reverse('magazine_author_detail',
                                             args=[self.bugs.pk, ])), -1)

        paul_dom_and_bugs = AuthorHolder(4, [self.paul, self.dom, self.bugs, ])
        result = render_to_string('magazine/_authors.html',
                                  {'object': paul_dom_and_bugs})
        self.assertEqual(striptags(result).strip(),
                         'Paul Beasley-Murray, Dominic Rodger and Bugs')
        self.assertNotEqual(result.find(self.paul.get_absolute_url()), -1)
        self.assertNotEqual(result.find(self.dom.get_absolute_url()), -1)
        # Bugs is not indexable, and so should have a link to his profile
        self.assertEqual(result.find(reverse('magazine_author_detail',
                                             args=[self.bugs.pk, ])), -1)
