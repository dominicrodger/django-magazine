from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from magazine.models import Author, Issue, Article
from magazine.tests.test_utils import initialise_article_text, LoginGuard

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
            self.staff_user = User.objects.create_user('staff', 'staff@internal.com', 'password')
            self.staff_user.is_staff = True
            self.staff_user.save()

        if not hasattr(self, 'user'):
            self.user = User.objects.create_user('nonstaff', 'nonstaff@external.com', 'password')

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
        with LoginGuard(self.client, 'nonstaff', 'password'):
            response = self.client.get(reverse('magazine_issue_detail', args=[2]))
            self.assertEqual(response.status_code, 404)

        # ... but does you're logged in as a staff member
        with LoginGuard(self.client, 'staff', 'password'):
            response = self.client.get(reverse('magazine_issue_detail', args=[2]))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['issue'], self.issue_3)
            self.assertEqual(list(response.context['articles']), [self.article_4,])

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
        with LoginGuard(self.client, 'nonstaff', 'password'):
            response = self.client.get(reverse('magazine_article_detail', args=[2, 4]))
            self.assertEqual(response.status_code, 404)

        # ... but does if you're logged in as a staff member
        with LoginGuard(self.client, 'staff', 'password'):
            response = self.client.get(reverse('magazine_article_detail', args=[2, 4]))
            self.assertEqual(response.status_code, 200)

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
        self.assertEqual(list(response.context['articles']), [self.article_5,self.article_1])
        self.assertContains(response, u'Paul Beasley-Murray')
        self.assertContains(response, self.article_1.get_absolute_url())
        self.assertContains(response, self.article_5.get_absolute_url())

        response = self.client.get(reverse('magazine_author_detail', args=[2,]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['author'], self.author_2)
        self.assertEqual(list(response.context['articles']), [self.article_3, self.article_5, self.article_2])
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
        with LoginGuard(self.client, 'nonstaff', 'password'):
            response = self.client.get(reverse('magazine_author_detail', args=[2,]))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(list(response.context['articles']), [self.article_3, self.article_5, self.article_2])

        # Check that you can see articles from unpublished issues if you're
        # logged in as a staff member
        with LoginGuard(self.client, 'staff', 'password'):
            response = self.client.get(reverse('magazine_author_detail', args=[2,]))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(list(response.context['articles']), [self.article_4, self.article_3, self.article_5, self.article_2])

    def testIssueListView(self):
        response = self.client.get(reverse('magazine_issues'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['issues']), [self.issue_2, self.issue_1])

        # Check that you can't see unpublished issues if you're logged in as a
        # regular user
        with LoginGuard(self.client, 'nonstaff', 'password'):
            response = self.client.get(reverse('magazine_issues'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(list(response.context['issues']), [self.issue_2, self.issue_1])

        # Check that you can see unpublished issues if you're logged in as a
        # staff member
        with LoginGuard(self.client, 'staff', 'password'):
            response = self.client.get(reverse('magazine_issues'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(list(response.context['issues']), [self.issue_3, self.issue_2, self.issue_1])
