from django.core.urlresolvers import reverse
from django.template import Context, Template
from django.template.defaultfilters import striptags
from django.test import TestCase
from magazine.models import Author, Article
from magazine.tests.test_utils import initialise_article_text


class MagazineFiltersTestCase(TestCase):
    fixtures = ['test_issues.json',
                'test_authors.json',
                'test_articles.json', ]

    def setUp(self):
        initialise_article_text()

        self.article_by_paul = Article.objects.get(pk=1)
        self.article_by_dom_and_paul = Article.objects.get(pk=5)

    def testAmpersandsNormal(self):
        t = Template("{% load magazine_tags %}{{ title|ampersands }}")
        self.assertEqual(t.render(Context({"title": "Normal & Usage"})),
                         "Normal <span class=\"ampersand\">&amp;</span> Usage")
        self.assertEqual(t.render(Context({"title": "Normal and Usage"})),
                         "Normal <span class=\"ampersand\">&amp;</span> Usage")

    def testAmpersandsAutoescape(self):
        t = Template("{% load magazine_tags %}"
                     "{% autoescape off %}"
                     "{{ title|ampersands }}"
                     "{% endautoescape %}")
        self.assertEqual(t.render(Context({"title": "Autoescape & Usage"})),
                         "Autoescape "
                         "<span class=\"ampersand\">&amp;</span> "
                         "Usage")
        self.assertEqual(t.render(Context({"title": "Autoescape and Usage"})),
                         "Autoescape "
                         "<span class=\"ampersand\">&amp;</span> "
                         "Usage")


class MagazineTagsTestCase(TestCase):
    fixtures = ['test_authors.json', ]

    def setUp(self):
        self.paul = Author.objects.get(pk=1)
        self.paul_url = self.paul.get_absolute_url()
        self.dom = Author.objects.get(pk=2)
        self.dom_url = self.dom.get_absolute_url()
        self.bugs = Author.objects.get(pk=3)
        self.bugs_url = reverse('magazine_author_detail',
                                args=[self.bugs.pk, ])

    def testAuthorTemplate(self):
        class AuthorHolder(object):
            def __init__(self, pk, authors):
                self.pk = pk
                self.authors = authors

            def all_authors(self):
                return self.authors

        t = Template("{% load magazine_tags %}{% magazine_authors object %}")
        self.assertEqual(t.render(Context({'object': AuthorHolder(1, [])})),
                         '')

        result = t.render(Context({'object': AuthorHolder(2, [self.paul, ])}))
        self.assertEqual(striptags(result),
                         'Paul Beasley-Murray')
        self.assertNotEqual(result.find(self.paul_url), -1)
        self.assertEqual(result.find(self.dom_url), -1)
        self.assertEqual(result.find(self.bugs_url), -1)

        paul_and_dom = AuthorHolder(3, [self.paul, self.dom, ])
        result = t.render(Context({'object': paul_and_dom}))
        self.assertEqual(striptags(result),
                         'Paul Beasley-Murray and Dominic Rodger')
        self.assertNotEqual(result.find(self.paul_url), -1)
        self.assertNotEqual(result.find(self.dom_url), -1)
        self.assertEqual(result.find(self.bugs_url), -1)

        paul_dom_and_bugs = AuthorHolder(4, [self.paul, self.dom, self.bugs, ])
        result = t.render(Context({'object': paul_dom_and_bugs}))
        self.assertEqual(striptags(result),
                         'Paul Beasley-Murray, Dominic Rodger and Bugs')
        self.assertNotEqual(result.find(self.paul_url), -1)
        self.assertNotEqual(result.find(self.dom_url), -1)
        # Bugs is not indexable, and so should not have a link to his profile
        self.assertEqual(result.find(self.bugs_url), -1)
