from django.core.urlresolvers import reverse
from django.test import TestCase
from magazine.models import Article, Author
from magazine.tests.test_utils import initialise_article_text


class ArticleTestCase(TestCase):
    fixtures = ['test_issues.json',
                'test_authors.json',
                'test_articles.json', ]

    def setUp(self):
        initialise_article_text()
        self.article_1 = Article.objects.get(pk=1)
        self.article_2 = Article.objects.get(pk=2)
        self.article_3 = Article.objects.get(pk=3)
        self.author_1 = Author.objects.get(pk=1)
        self.author_2 = Author.objects.get(pk=2)
        self.author_3 = Author.objects.get(pk=3)

    def testUnicode(self):
        self.assertEqual(self.article_1.__unicode__(), u'My first article')
        self.assertEqual(self.article_2.__unicode__(), u'My second article')
        self.assertEqual(self.article_3.__unicode__(), u'My third article')

    def testMarkVisited(self):
        self.assertEqual(self.article_1.hits, 0)
        self.article_1.mark_visited()
        self.article_1 = Article.objects.get(pk=1)
        self.assertEqual(self.article_1.hits, 1)
        self.article_1.mark_visited()
        self.article_1 = Article.objects.get(pk=1)
        self.assertEqual(self.article_1.hits, 2)

    def testTeaser(self):
        self.assertEqual(self.article_1.teaser(),
                         u'Witty description of the first article')
        self.assertEqual(self.article_2.teaser(),
                         u'Full text of the second article. Lorem ipsum dolor '
                         'sit amet, consectetur adipisicing elit, sed do '
                         'eiusmod tempor incididunt ut labore et dolore '
                         'magna aliqua. Ut enim ad minim veniam, quis '
                         'nostrud exercitation ullamco laboris nisi ut '
                         'aliquip ex ea commodo consequat. Duis aute irure '
                         'dolor in reprehenderit in voluptate ...')
        self.assertEqual(self.article_3.teaser(), u'None available.')

    def testGetURL(self):
        self.assertEqual(self.article_1.get_absolute_url(),
                         reverse('magazine_article_detail',
                                 args=[self.article_1.issue.number,
                                       self.article_1.pk, ]))

        self.assertEqual(self.article_2.get_absolute_url(),
                         reverse('magazine_article_detail',
                                 args=[self.article_2.issue.number,
                                       self.article_2.pk, ]))

    def testFetchingArticleIssuesIsFree(self):
        articles = Article.objects.all()

        for article in articles:
            self.assertNumQueries(0, lambda: getattr(article, 'issue'))

    def testNumArticles(self):
        self.assertNumQueries(0, lambda: getattr(self.author_1,
                                                 'num_articles'))
        self.assertNumQueries(0, lambda: getattr(self.author_2,
                                                 'num_articles'))
        self.assertNumQueries(0, lambda: getattr(self.author_3,
                                                 'num_articles'))

        self.assertEqual(self.author_1.num_articles, 2)
        self.assertEqual(self.author_2.num_articles, 4)
        self.assertEqual(self.author_3.num_articles, 0)

        local_author_1 = Author.plain_objects.get(pk=1)
        self.assertNumQueries(1, local_author_1.get_num_articles)
        self.assertNumQueries(0, local_author_1.get_num_articles)
        self.assertEqual(local_author_1.num_articles, 2)

    def testNumAuthors(self):
        articles = Article.objects_with_num_authors.all()

        expected_num_authors = [1, 1, 1, 2, 1]

        for article in articles:
            self.assertNumQueries(0, lambda: getattr(article, 'num_authors'))

        self.assertEqual(expected_num_authors,
                         [a.num_authors for a in articles])
