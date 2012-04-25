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

    def testAmpersands(self):
        t = Template("{% load magazine_tags %}{{ title|ampersands }}")
        c = Context({"title": "Test & Something"})
        expected = "Test <span class=\"ampersand\">&amp;</span> Something"
        self.assertEqual(expected, t.render(c))

        t = Template("{% load magazine_tags %}{% autoescape off %}{{ title|ampersands }}{% endautoescape %}")
        c = Context({"title": "Test & Something"})
        expected = "Test & Something"
        self.assertEqual(expected, t.render(c))
