from django.core.urlresolvers import reverse
from django.test import TestCase
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
