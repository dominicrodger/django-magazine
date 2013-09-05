from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from magazine.models import Author, Issue, Article
from magazine.tests.test_utils import initialise_article_text, LoginGuard


class MagazineGeneralViewsTestCase(TestCase):
    fixtures = ['test_issues.json',
                'test_authors.json',
                'test_articles.json', ]

    def setUp(self):
        initialise_article_text()

        self.article_by_paul = Article.objects.get(pk=1)
        self.article_by_dom = Article.objects.get(pk=2)
        self.article_by_dom_issue_2 = Article.objects.get(pk=3)
        self.article_by_dom_unpublished = Article.objects.get(pk=4)
        self.article_by_dom_and_paul = Article.objects.get(pk=5)
        self.issue_1 = Issue.objects.get(pk=1)
        self.issue_2 = Issue.objects.get(pk=2)
        self.issue_3_unpublished = Issue.objects.get(pk=3)
        self.paul = Author.objects.get(pk=1)
        self.dominic = Author.objects.get(pk=2)
        self.bugs = Author.objects.get(pk=3)

        if not hasattr(self, 'staff_user'):
            self.staff_user = User.objects.create_user('staff',
                                                       'staff@internal.com',
                                                       'password')
            self.staff_user.is_staff = True
            self.staff_user.save()

        if not hasattr(self, 'user'):
            self.user = User.objects.create_user('nonstaff',
                                                 'nonstaff@external.com',
                                                 'password')

    def testIndexView(self):
        response = self.client.get(reverse('magazine_index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['current_articles']),
                         [self.article_by_dom_issue_2,
                          self.article_by_dom_and_paul, ])
        self.assertEqual(response.context['current_issue'], self.issue_2)
        self.assertNotContains(response, self.article_by_paul.teaser())
        self.assertNotContains(response, self.article_by_dom.teaser())
        self.assertContains(response, self.article_by_dom_issue_2.teaser())
        self.assertContains(response, self.article_by_dom_and_paul.teaser())

        self.issue_2.published = False
        self.issue_2.save()

        response = self.client.get(reverse('magazine_index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['current_articles']),
                         [self.article_by_paul, self.article_by_dom, ])
        self.assertEqual(response.context['current_issue'], self.issue_1)
        self.assertContains(response, self.article_by_paul.teaser())
        self.assertContains(response, self.article_by_dom.teaser())
        self.assertNotContains(response, self.article_by_dom_issue_2.teaser())

        self.issue_2.published = True
        self.issue_2.save()

    def testIssueDetailView(self):
        response = self.client.get(reverse('magazine_issue_detail', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['issue'], self.issue_1)
        self.assertEqual(list(response.context['articles']),
                         [self.article_by_paul, self.article_by_dom])
        self.assertContains(response,
                            self.article_by_paul.authors.all()[0].
                            __unicode__())
        self.assertContains(response,
                            self.article_by_dom.authors.all()[0].__unicode__())
        self.assertContains(response,
                            self.article_by_paul.authors.all()[0].
                            get_absolute_url())
        self.assertContains(response,
                            self.article_by_dom.authors.all()[0].
                            get_absolute_url())

        # Check that changing the order of the articles in an issue affects the
        # order they are rendered.
        old_order_in_issue = self.article_by_paul.order_in_issue
        self.article_by_paul.order_in_issue = 5
        self.article_by_paul.save()

        response = self.client.get(reverse('magazine_issue_detail', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['issue'], self.issue_1)
        self.assertEqual(list(response.context['articles']),
                         [self.article_by_dom, self.article_by_paul])

        self.article_by_paul.order_in_issue = old_order_in_issue
        self.article_by_paul.save()

        # Check that trying to fetch an issue that isn't yet published
        # results in a 404
        response = self.client.get(reverse('magazine_issue_detail', args=[2]))
        self.assertEqual(response.status_code, 404)

        # ... still doesn't work if you login as a regular user
        with LoginGuard(self.client, 'nonstaff'):
            response = self.client.get(reverse('magazine_issue_detail',
                                               args=[2]))
            self.assertEqual(response.status_code, 404)

        # ... but does you're logged in as a staff member
        with LoginGuard(self.client, 'staff'):
            response = self.client.get(reverse('magazine_issue_detail',
                                               args=[2]))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['issue'],
                             self.issue_3_unpublished)
            self.assertEqual(list(response.context['articles']),
                             [self.article_by_dom_unpublished, ])

        response = self.client.get(reverse('magazine_issue_detail', args=[3]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['issue'], self.issue_2)
        self.assertEqual(list(response.context['articles']),
                         [self.article_by_dom_issue_2,
                          self.article_by_dom_and_paul, ])

        response = self.client.get(reverse('magazine_issue_detail', args=[4]))
        self.assertEqual(response.status_code, 404)

    def testArticleDetailView(self):
        response = self.client.get(reverse('magazine_article_detail',
                                           args=[1, 1]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['issue'], self.issue_1)
        self.assertEqual(response.context['article'], self.article_by_paul)
        self.assertContains(response, self.article_by_paul.title)

        # Check that we've updated hit counts.
        self.assertEqual(Article.objects.get(pk=self.article_by_paul.pk).hits,
                         1)
        response = self.client.get(reverse('magazine_article_detail',
                                           args=[1, 1]))
        self.assertEqual(Article.objects.get(pk=self.article_by_paul.pk).hits,
                         2)

        # Check for fetching an article for an issue number where
        # the primary key and the issue number don't line up.
        response = self.client.get(reverse('magazine_article_detail',
                                           args=[3, 3]))
        self.assertEqual(response.status_code, 200)
        # Issue with pk 2 has number 3
        self.assertEqual(response.context['issue'], self.issue_2)
        self.assertEqual(response.context['article'],
                         self.article_by_dom_issue_2)

        # Check that fetching an article by the wrong issue number
        # results in a 404.
        response = self.client.get(reverse('magazine_article_detail',
                                           args=[2, 2]))
        self.assertEqual(response.status_code, 404)

        # Check that fetching an article by a non-existent issue
        # number results in a 404.
        response = self.client.get(reverse('magazine_article_detail',
                                           args=[300, 2]))
        self.assertEqual(response.status_code, 404)

        # Check that fetching an article that doesn't exist
        # results in a 404.
        response = self.client.get(reverse('magazine_article_detail',
                                           args=[1, 200]))
        self.assertEqual(response.status_code, 404)

        # Check that fetching an article for an issue that
        # isn't yet published results in a 404.
        response = self.client.get(reverse('magazine_article_detail',
                                           args=[2, 4]))
        self.assertEqual(response.status_code, 404)

        # ... still doesn't work if you login as a regular user
        with LoginGuard(self.client, 'nonstaff'):
            response = self.client.get(reverse('magazine_article_detail',
                                               args=[2, 4]))
            self.assertEqual(response.status_code, 404)

        # ... but does if you're logged in as a staff member
        with LoginGuard(self.client, 'staff'):
            response = self.client.get(reverse('magazine_article_detail',
                                               args=[2, 4]))
            self.assertEqual(response.status_code, 200)

        # Check that the full text is rendered
        response = self.client.get(reverse('magazine_article_detail',
                                           args=[1, 2]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['issue'], self.issue_1)
        self.assertEqual(response.context['article'], self.article_by_dom)
        self.assertContains(response, self.article_by_dom.text)
        # Check that the author details show up (if they exist)
        for author in self.article_by_dom.authors.all():
            self.assertContains(response, author)
            self.assertContains(response, author.details)
            self.assertContains(response, author.get_absolute_url())

        # Check that headings are demoted (h1 -> h2, h2 -> h3 etc)
        response = self.client.get(reverse('magazine_article_detail',
                                           args=[3, 5]))
        self.assertContains(response, '<h2>Heading 1</h2>')
        self.assertContains(response, '<h3>Heading 2</h3>')
        self.assertContains(response, '<h4>Heading 3</h4>')
        self.assertContains(response, '<h5>Heading 4</h5>')
        self.assertContains(response, '<h6>Heading 5</h6>')

    def testAuthorDetailView(self):
        response = self.client.get(reverse('magazine_author_detail',
                                           args=[1, ]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['author'], self.paul)
        self.assertEqual(list(response.context['articles']),
                         [self.article_by_dom_and_paul, self.article_by_paul])
        self.assertContains(response, u'Paul Beasley-Murray')
        self.assertContains(response, self.article_by_paul.get_absolute_url())
        self.assertContains(response,
                            self.article_by_dom_and_paul.get_absolute_url())

        response = self.client.get(reverse('magazine_author_detail',
                                           args=[2, ]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['author'], self.dominic)
        self.assertEqual(list(response.context['articles']),
                         [self.article_by_dom_issue_2,
                          self.article_by_dom_and_paul,
                          self.article_by_dom, ])
        self.assertContains(response, u'Dominic Rodger')
        self.assertNotContains(response,
                               self.article_by_paul.get_absolute_url())
        self.assertContains(response, self.article_by_dom.get_absolute_url())
        self.assertContains(response,
                            self.article_by_dom_issue_2.get_absolute_url())

        # Bugs Bunny is not indexable
        response = self.client.get(reverse('magazine_author_detail',
                                           args=[3, ]))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('magazine_author_detail',
                                           args=[4, ]))
        self.assertEqual(response.status_code, 404)

        # Check that you can't see articles from unpublished issues if you're
        # logged in as a regular user
        with LoginGuard(self.client, 'nonstaff'):
            response = self.client.get(reverse('magazine_author_detail',
                                               args=[2, ]))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(list(response.context['articles']),
                             [self.article_by_dom_issue_2,
                              self.article_by_dom_and_paul,
                              self.article_by_dom])

        # Check that you can see articles from unpublished issues if you're
        # logged in as a staff member
        with LoginGuard(self.client, 'staff'):
            response = self.client.get(reverse('magazine_author_detail',
                                               args=[2, ]))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(list(response.context['articles']),
                             [self.article_by_dom_unpublished,
                              self.article_by_dom_issue_2,
                              self.article_by_dom_and_paul,
                              self.article_by_dom])

    def testIssueListView(self):
        response = self.client.get(reverse('magazine_issues'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['issues']),
                         [self.issue_2, self.issue_1])

        # Check that you can't see unpublished issues if you're logged in as a
        # regular user
        with LoginGuard(self.client, 'nonstaff'):
            response = self.client.get(reverse('magazine_issues'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(list(response.context['issues']),
                             [self.issue_2, self.issue_1])

        # Check that you can see unpublished issues if you're logged in as a
        # staff member
        with LoginGuard(self.client, 'staff'):
            response = self.client.get(reverse('magazine_issues'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(list(response.context['issues']),
                             [self.issue_3_unpublished,
                              self.issue_2,
                              self.issue_1])

    def testAuthorListView(self):
        response = self.client.get(reverse('magazine_authors'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.paul.surname)
        self.assertContains(response, self.dominic.surname)
        paul_index = response.content.index(self.paul.surname)
        dominic_index = response.content.index(self.dominic.surname)
        self.assertTrue(dominic_index < paul_index)

    def testAuthorListViewAlphabetised(self):
        response = self.client.get(reverse('magazine_authors_alphabetised'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.paul.surname)
        self.assertContains(response, self.dominic.surname)
        paul_index = response.content.index(self.paul.surname)
        dominic_index = response.content.index(self.dominic.surname)
        self.assertTrue(dominic_index > paul_index)

    def testAuthorArticlesListView(self):
        response = self.client.get(reverse('magazine_author_articles',
                                           args=[self.paul.pk, ]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.paul.forename)
        self.assertContains(response, self.article_by_paul.get_absolute_url())
        self.assertNotContains(response,
                               self.article_by_dom.get_absolute_url())
        self.assertNotContains(response,
                               self.article_by_dom_issue_2.get_absolute_url())
        self.assertNotContains(response,
                               self.article_by_dom_unpublished.
                               get_absolute_url())
        self.assertContains(response,
                            self.article_by_dom_and_paul.get_absolute_url())

        response = self.client.get(reverse('magazine_author_articles',
                                           args=[self.dominic.pk, ]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.dominic.forename)
        self.assertNotContains(response,
                               self.article_by_paul.get_absolute_url())
        self.assertContains(response, self.article_by_dom.get_absolute_url())
        self.assertContains(response,
                            self.article_by_dom_issue_2.get_absolute_url())
         # By author 2, but not published
        self.assertNotContains(response,
                               self.article_by_dom_unpublished.
                               get_absolute_url())
        self.assertContains(response,
                            self.article_by_dom_and_paul.get_absolute_url())

        response = self.client.get(reverse('magazine_author_articles',
                                           args=[self.bugs.pk, ]))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('magazine_author_articles',
                                           args=[73, ]))
        self.assertEqual(response.status_code, 404)
