from django.template import Context, Template
from django.test import TestCase
from magazine.models import Author, Issue, Article
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
        t = Template("{% load magazine_tags %}{% autoescape off %}{{ title|ampersands }}{% endautoescape %}")
        self.assertEqual(t.render(Context({"title": "Autoescape & Usage"})),
                         "Autoescape <span class=\"ampersand\">&amp;</span> Usage")
        self.assertEqual(t.render(Context({"title": "Autoescape and Usage"})),
                         "Autoescape <span class=\"ampersand\">&amp;</span> Usage")
