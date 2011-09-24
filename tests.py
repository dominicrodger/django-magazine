from datetime import date, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template.defaultfilters import striptags
from django.template.loader import render_to_string
from django.test import TestCase
from django.test.client import Client
from magazine.models import Author, Issue, Article, subtract_n_months

# Loading from fixtures doesn't call Article.save(), so the
# cleaned_text won't be populated. We therefore need to force
# it here.
def initialise_article_text():
    for article in Article.objects.all():
        if article.text and not article.cleaned_text:
            article.save()

class AuthorTestCase(TestCase):
    fixtures = ['test_authors.json',]

    def setUp(self):
        self.paul = Author.objects.get(pk = 1)
        self.dom  = Author.objects.get(pk = 2)
        self.bugs = Author.objects.get(pk = 3)

    def testUnicode(self):
        self.assertEqual(self.paul.__unicode__(), u'Paul Beasley-Murray')
        self.assertEqual(self.dom.__unicode__(), u'Dominic Rodger')

    def testGetURL(self):
        self.assertEqual(self.paul.get_absolute_url(), reverse('magazine_author_detail', args=[self.paul.pk,]))
        self.assertEqual(self.dom.get_absolute_url(), reverse('magazine_author_detail', args=[self.dom.pk,]))

    def testAuthorTemplate(self):
        result = (render_to_string('magazine/_authors.html', {'authors': []}))
        self.assertEqual(result.strip(), '')

        result = (render_to_string('magazine/_authors.html', {'authors': [self.paul,]}))
        self.assertEqual(striptags(result).strip(), 'Paul Beasley-Murray')
        self.assertNotEqual(result.find(self.paul.get_absolute_url()), -1)
        self.assertEqual(result.find(self.dom.get_absolute_url()), -1)
        self.assertEqual(result.find(reverse('magazine_author_detail', args=[self.bugs.pk,])), -1)

        result = render_to_string('magazine/_authors.html', {'authors': [self.paul,self.dom]})
        self.assertEqual(striptags(result).strip(), 'Paul Beasley-Murray and Dominic Rodger')
        self.assertNotEqual(result.find(self.paul.get_absolute_url()), -1)
        self.assertNotEqual(result.find(self.dom.get_absolute_url()), -1)
        self.assertEqual(result.find(reverse('magazine_author_detail', args=[self.bugs.pk,])), -1)

        result = render_to_string('magazine/_authors.html', {'authors': [self.paul, self.dom, self.bugs]})
        self.assertEqual(striptags(result).strip(), 'Paul Beasley-Murray, Dominic Rodger and Bugs')
        self.assertNotEqual(result.find(self.paul.get_absolute_url()), -1)
        self.assertNotEqual(result.find(self.dom.get_absolute_url()), -1)
        # Bugs is not indexable, and so should have a link to his profile
        self.assertEqual(result.find(reverse('magazine_author_detail', args=[self.bugs.pk,])), -1)

class IssueTestCase(TestCase):
    fixtures = ['test_issues.json',]

    def setUp(self):
        self.issue_1 = Issue.objects.get(pk = 1)
        self.issue_2 = Issue.objects.get(pk = 2)
        self.issue_3 = Issue.objects.get(pk = 3)

    def testUnicode(self):
        self.assertEqual(self.issue_1.__unicode__(), u'Issue 1')
        self.assertEqual(self.issue_2.__unicode__(), u'Issue 3')

    def testMonthYear(self):
        self.assertEqual(self.issue_1.month_year(), u'January 2010')
        self.assertEqual(self.issue_2.month_year(), u'April 2010')

    def testDefaultPublished(self):
        self.assertEqual(self.issue_1.published, True)
        self.assertEqual(self.issue_2.published, True)

    def testCurrentIssue(self):
        self.assertEqual(Issue.current_issue(), self.issue_2)
        self.issue_2.published = False
        self.issue_2.save()

        self.assertEqual(Issue.current_issue(), self.issue_1)

        self.issue_2.published = True
        self.issue_2.save()

    def testGetURL(self):
        self.assertEqual(self.issue_1.get_absolute_url(), reverse('magazine_issue_detail', args=[self.issue_1.number,]))
        self.assertEqual(self.issue_2.get_absolute_url(), reverse('magazine_issue_detail', args=[self.issue_2.number,]))

    def testFirstOfMonth(self):
        issue = Issue.objects.create(number = 4, issue_date = date(2010,4,30))
        issue_4 = Issue.objects.get(pk = issue.pk)
        self.assertEqual(issue.issue_date, date(2010,4,1))

    def testIssueEmbargoed(self):
        self.assertFalse(self.issue_1.embargoed())
        self.assertFalse(self.issue_2.embargoed())
        self.assertTrue(self.issue_3.embargoed())

        start_of_month = date.today().replace(day = 1)

        if int(getattr(settings, 'MAGAZINE_EMBARGO_TIME_IN_MONTHS', 2)) > 0:
            issue = Issue.objects.create(number = 4, issue_date = start_of_month - timedelta(days = 20))
            issue_4 = Issue.objects.get(pk = issue.pk)
            self.assertTrue(issue_4.embargoed())

            issue_4.issue_date = subtract_n_months(start_of_month, int(getattr(settings, 'MAGAZINE_EMBARGO_TIME_IN_MONTHS', 2)) - 1)
            issue_4.save()
            self.assertTrue(issue_4.embargoed())

            issue_4.issue_date = subtract_n_months(start_of_month, int(getattr(settings, 'MAGAZINE_EMBARGO_TIME_IN_MONTHS', 2)))
            issue_4.save()
            self.assertFalse(issue_4.embargoed())

class ArticleTestCase(TestCase):
    fixtures = ['test_issues.json', 'test_authors.json', 'test_articles.json',]

    def setUp(self):
        initialise_article_text()
        self.article_1 = Article.objects.get(pk = 1)
        self.article_2 = Article.objects.get(pk = 2)
        self.article_3 = Article.objects.get(pk = 3)
        self.author_1 = Author.objects.get(pk = 1)
        self.author_2 = Author.objects.get(pk = 2)
        self.author_3 = Author.objects.get(pk = 3)

    def testUnicode(self):
        self.assertEqual(self.article_1.__unicode__(), u'My first article')
        self.assertEqual(self.article_2.__unicode__(), u'My second article')
        self.assertEqual(self.article_3.__unicode__(), u'My third article')

    def testMarkVisited(self):
        self.assertEqual(self.article_1.hits, 0)
        self.article_1.mark_visited()
        self.article_1 = Article.objects.get(pk = 1)
        self.assertEqual(self.article_1.hits, 1)
        self.article_1.mark_visited()
        self.article_1 = Article.objects.get(pk = 1)
        self.assertEqual(self.article_1.hits, 2)

    def testTeaser(self):
        self.assertEqual(self.article_1.teaser(), u'Witty description of the first article')
        self.assertEqual(self.article_2.teaser(), u'Full text of the second article. Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate ...')
        self.assertEqual(self.article_3.teaser(), u'None available.')

    def testGetURL(self):
        self.assertEqual(self.article_1.get_absolute_url(), reverse('magazine_article_detail', args=[self.article_1.issue.number, self.article_1.pk,]))
        self.assertEqual(self.article_2.get_absolute_url(), reverse('magazine_article_detail', args=[self.article_2.issue.number, self.article_2.pk,]))

    def testFetchingArticleIssuesIsFree(self):
        articles = Article.objects.all()

        for article in articles:
            self.assertNumQueries(0, lambda: getattr(article, 'issue'))

    def testNumArticles(self):
        self.assertNumQueries(0, lambda: getattr(self.author_1, 'num_articles'))
        self.assertNumQueries(0, lambda: getattr(self.author_2, 'num_articles'))
        self.assertNumQueries(0, lambda: getattr(self.author_3, 'num_articles'))

        self.assertEqual(self.author_1.num_articles, 2)
        self.assertEqual(self.author_2.num_articles, 4)
        self.assertEqual(self.author_3.num_articles, 0)

    def testNumAuthors(self):
        articles = Article.objects_with_num_authors.all()

        expected_num_authors = [1, 1, 1, 2, 1]

        for article in articles:
            self.assertNumQueries(0, lambda: getattr(article, 'num_authors'))

        self.assertEqual(expected_num_authors, [a.num_authors for a in articles])

class MagazineGeneralViewsTestCase(TestCase):
    fixtures = ['test_issues.json', 'test_authors.json', 'test_articles.json',]

    def setUp(self):
        initialise_article_text()

        self.article_1 = Article.objects.get(pk = 1)
        self.article_2 = Article.objects.get(pk = 2)
        self.article_3 = Article.objects.get(pk = 3)
        self.article_4 = Article.objects.get(pk = 4)
        self.article_5 = Article.objects.get(pk = 5)
        self.issue_1 = Issue.objects.get(pk = 1)
        self.issue_2 = Issue.objects.get(pk = 2)
        self.issue_3 = Issue.objects.get(pk = 3)
        self.author_1 = Author.objects.get(pk = 1)
        self.author_2 = Author.objects.get(pk = 2)

        if not hasattr(self, 'staff_user'):
            self.staff_user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
            self.staff_user.is_staff = True
            self.staff_user.save()

        if not hasattr(self, 'user'):
            self.user = User.objects.create_user('ringo', 'starr@thebeatles.com', 'ringopassword')

    def testIndexView(self):
        response = self.client.get(reverse('magazine_index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['current_articles']), [self.article_3, self.article_5])
        self.assertEqual(response.context['current_issue'], self.issue_2)
        self.assertNotContains(response, self.article_1.teaser())
        self.assertNotContains(response, self.article_2.teaser())
        self.assertContains(response, self.article_3.teaser())
        self.assertContains(response, self.article_5.teaser())

        self.issue_2.published = False
        self.issue_2.save()

        response = self.client.get(reverse('magazine_index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['current_articles']), [self.article_1, self.article_2])
        self.assertEqual(response.context['current_issue'], self.issue_1)
        self.assertContains(response, self.article_1.teaser())
        self.assertContains(response, self.article_2.teaser())
        self.assertNotContains(response, self.article_3.teaser())

        self.issue_2.published = True
        self.issue_2.save()

    def testIssueDetailView(self):
        response = self.client.get(reverse('magazine_issue_detail', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['issue'], self.issue_1)
        self.assertEqual(list(response.context['articles']), [self.article_1, self.article_2])
        self.assertContains(response, self.article_1.authors.all()[0].__unicode__())
        self.assertContains(response, self.article_2.authors.all()[0].__unicode__())
        self.assertContains(response, self.article_1.authors.all()[0].get_absolute_url())
        self.assertContains(response, self.article_2.authors.all()[0].get_absolute_url())

        # Check that changing the order of the articles in an issue affects the
        # order they are rendered.
        old_order_in_issue = self.article_1.order_in_issue
        self.article_1.order_in_issue = 5
        self.article_1.save()

        response = self.client.get(reverse('magazine_issue_detail', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['issue'], self.issue_1)
        self.assertEqual(list(response.context['articles']), [self.article_2, self.article_1])

        self.article_1.order_in_issue = old_order_in_issue
        self.article_1.save()

        # Check that trying to fetch an issue that isn't yet published
        # results in a 404
        response = self.client.get(reverse('magazine_issue_detail', args=[2]))
        self.assertEqual(response.status_code, 404)

        # ... still doesn't work if you login as a regular user
        self.client.login(username='ringo', password='ringopassword')
        response = self.client.get(reverse('magazine_issue_detail', args=[2]))
        self.assertEqual(response.status_code, 404)
        self.client.logout()

        # ... but does you're logged in as a staff member
        self.client.login(username='john', password='johnpassword')
        response = self.client.get(reverse('magazine_issue_detail', args=[2]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['issue'], self.issue_3)
        self.assertEqual(list(response.context['articles']), [self.article_4,])
        self.client.logout()

        response = self.client.get(reverse('magazine_issue_detail', args=[3]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['issue'], self.issue_2)
        self.assertEqual(list(response.context['articles']), [self.article_3, self.article_5])

        response = self.client.get(reverse('magazine_issue_detail', args=[4]))
        self.assertEqual(response.status_code, 404)

    def testArticleDetailView(self):
        response = self.client.get(reverse('magazine_article_detail', args=[1, 1]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['issue'], self.issue_1)
        self.assertEqual(response.context['article'], self.article_1)
        self.assertContains(response, self.article_1.title)

        # Check that we've updated hit counts.
        self.assertEqual(Article.objects.get(pk = self.article_1.pk).hits, 1)
        response = self.client.get(reverse('magazine_article_detail', args=[1, 1]))
        self.assertEqual(Article.objects.get(pk = self.article_1.pk).hits, 2)

        # Check for fetching an article for an issue number where
        # the primary key and the issue number don't line up.
        response = self.client.get(reverse('magazine_article_detail', args=[3, 3]))
        self.assertEqual(response.status_code, 200)
        # Issue with pk 2 has number 3
        self.assertEqual(response.context['issue'], self.issue_2)
        self.assertEqual(response.context['article'], self.article_3)

        # Check that fetching an article by the wrong issue number
        # results in a 404.
        response = self.client.get(reverse('magazine_article_detail', args=[2, 2]))
        self.assertEqual(response.status_code, 404)

        # Check that fetching an article by a non-existent issue
        # number results in a 404.
        response = self.client.get(reverse('magazine_article_detail', args=[300, 2]))
        self.assertEqual(response.status_code, 404)

        # Check that fetching an article that doesn't exist
        # results in a 404.
        response = self.client.get(reverse('magazine_article_detail', args=[1, 200]))
        self.assertEqual(response.status_code, 404)

        # Check that fetching an article for an issue that
        # isn't yet published results in a 404.
        response = self.client.get(reverse('magazine_article_detail', args=[2, 4]))
        self.assertEqual(response.status_code, 404)

        # ... still doesn't work if you login as a regular user
        self.client.login(username='ringo', password='ringopassword')
        response = self.client.get(reverse('magazine_article_detail', args=[2, 4]))
        self.assertEqual(response.status_code, 404)
        self.client.logout()

        # ... but does if you're logged in as a staff member
        self.client.login(username='john', password='johnpassword')
        response = self.client.get(reverse('magazine_article_detail', args=[2, 4]))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        # Check that the full text is rendered
        response = self.client.get(reverse('magazine_article_detail', args=[1, 2]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['issue'], self.issue_1)
        self.assertEqual(response.context['article'], self.article_2)
        self.assertContains(response, self.article_2.text)
        # Check that the author details show up (if they exist)
        for author in self.article_2.authors.all():
            self.assertContains(response, author)
            self.assertContains(response, author.details)
            self.assertContains(response, author.get_absolute_url())

        # Check that headings are demoted (h1 -> h2, h2 -> h3 etc)
        response = self.client.get(reverse('magazine_article_detail', args=[3, 5]))
        self.assertContains(response, '<h2>Heading 1</h2>')
        self.assertContains(response, '<h3>Heading 2</h3>')
        self.assertContains(response, '<h4>Heading 3</h4>')
        self.assertContains(response, '<h5>Heading 4</h5>')
        self.assertContains(response, '<h6>Heading 5</h6>')

    def testAuthorDetailView(self):
        response = self.client.get(reverse('magazine_author_detail', args=[1,]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['author'], self.author_1)
        self.assertEqual(list(response.context['articles']), [self.article_1,self.article_5])
        self.assertContains(response, u'Paul Beasley-Murray')
        self.assertContains(response, self.article_1.get_absolute_url())
        self.assertContains(response, self.article_5.get_absolute_url())

        response = self.client.get(reverse('magazine_author_detail', args=[2,]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['author'], self.author_2)
        self.assertEqual(list(response.context['articles']), [self.article_2, self.article_3, self.article_5])
        self.assertContains(response, u'Dominic Rodger')
        self.assertNotContains(response, self.article_1.get_absolute_url())
        self.assertContains(response, self.article_2.get_absolute_url())
        self.assertContains(response, self.article_3.get_absolute_url())

        # Bugs Bunny is not indexable
        response = self.client.get(reverse('magazine_author_detail', args=[3,]))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('magazine_author_detail', args=[4,]))
        self.assertEqual(response.status_code, 404)

        # Check that you can't see articles from unpublished issues if you're
        # logged in as a regular user
        self.client.login(username='ringo', password='ringopassword')
        response = self.client.get(reverse('magazine_author_detail', args=[2,]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['articles']), [self.article_2, self.article_3, self.article_5])
        self.client.logout()

        # Check that you can see articles from unpublished issues if you're
        # logged in as a staff member
        self.client.login(username='john', password='johnpassword')
        response = self.client.get(reverse('magazine_author_detail', args=[2,]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['articles']), [self.article_2, self.article_3, self.article_5, self.article_4])
        self.client.logout()

    def testIssueListView(self):
        response = self.client.get(reverse('magazine_issues'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['issues']), [self.issue_2, self.issue_1])

        # Check that you can't see unpublished issues if you're logged in as a
        # regular user
        self.client.login(username='ringo', password='ringopassword')
        response = self.client.get(reverse('magazine_issues'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['issues']), [self.issue_2, self.issue_1])
        self.client.logout()

        # Check that you can see unpublished issues if you're logged in as a
        # staff member
        self.client.login(username='john', password='johnpassword')
        response = self.client.get(reverse('magazine_issues'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['issues']), [self.issue_3, self.issue_2, self.issue_1])
        self.client.logout()

class SubtractNMonthsTestCase(TestCase):

    def testWithDateAtMiddleOfYear(self):
        self.assertEqual(subtract_n_months(date(2010, 4, 7), 2), date(2010, 2, 7))

    def testWithDateAtEndOfMonth(self):
        # September only has 30 days
        self.assertEqual(subtract_n_months(date(2010, 10, 31), 1), date(2010, 9, 30))

    def testWithDateAtBeginningOfYear(self):
        self.assertEqual(subtract_n_months(date(2010, 1, 31), 1), date(2009, 12, 31))

    def testWithDateAtBeginningOfYearAtEndOfMonth(self):
        self.assertEqual(subtract_n_months(date(2010, 3, 31), 4), date(2009, 11, 30))

    def testWithMoreThan12Months(self):
        self.assertEqual(subtract_n_months(date(2010, 3, 31), 25), date(2008, 2, 29))
        self.assertEqual(subtract_n_months(date(2010, 3, 31), 37), date(2007, 2, 28))
