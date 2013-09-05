from datetime import date, timedelta
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from magazine.models import Issue, subtract_n_months


class NoIssuesTestCase(TestCase):
    def testLiveIssues(self):
        self.assertEqual(Issue.current_issue(), None)


class IssueTestCase(TestCase):
    fixtures = ['test_issues.json', ]

    def setUp(self):
        self.issue_1 = Issue.objects.get(pk=1)
        self.issue_2 = Issue.objects.get(pk=2)
        self.issue_3 = Issue.objects.get(pk=3)

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
        self.assertEqual(self.issue_1.get_absolute_url(),
                         reverse('magazine_issue_detail',
                                 args=[self.issue_1.number, ]))
        self.assertEqual(self.issue_2.get_absolute_url(),
                         reverse('magazine_issue_detail',
                                 args=[self.issue_2.number, ]))

    def testFirstOfMonth(self):
        issue = Issue.objects.create(number=4,
                                     issue_date=date(2010, 4, 30))
        Issue.objects.get(pk=issue.pk)
        self.assertEqual(issue.issue_date,
                         date(2010, 4, 1))

    def testIssueEmbargoed(self):
        self.assertFalse(self.issue_1.embargoed())
        self.assertFalse(self.issue_2.embargoed())
        self.assertTrue(self.issue_3.embargoed())

        start_of_month = date.today().replace(day=1)

        if int(getattr(settings, 'MAGAZINE_EMBARGO_TIME_IN_MONTHS', 2)) > 0:
            twenty_d_from_start = start_of_month - timedelta(days=20)
            issue = Issue.objects.create(number=4,
                                         issue_date=twenty_d_from_start)
            issue_4 = Issue.objects.get(pk=issue.pk)
            self.assertTrue(issue_4.embargoed())

            embargo_key = 'MAGAZINE_EMBARGO_TIME_IN_MONTHS'
            magazine_embargo_months = int(getattr(settings,
                                                  embargo_key, 2))
            issue_4.issue_date = subtract_n_months(start_of_month,
                                                   magazine_embargo_months - 1)
            issue_4.save()
            self.assertTrue(issue_4.embargoed())

            issue_4.issue_date = subtract_n_months(start_of_month,
                                                   magazine_embargo_months)
            issue_4.save()
            self.assertFalse(issue_4.embargoed())
