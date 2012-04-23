from datetime import date
from django.test import TestCase
from magazine.models import subtract_n_months


class SubtractNMonthsTestCase(TestCase):
    def testWithDateAtMiddleOfYear(self):
        self.assertEqual(subtract_n_months(date(2010, 4, 7), 2),
                         date(2010, 2, 7))

    def testWithDateAtEndOfMonth(self):
        # September only has 30 days
        self.assertEqual(subtract_n_months(date(2010, 10, 31), 1),
                         date(2010, 9, 30))

    def testWithDateAtBeginningOfYear(self):
        self.assertEqual(subtract_n_months(date(2010, 1, 31), 1),
                         date(2009, 12, 31))

    def testWithDateAtBeginningOfYearAtEndOfMonth(self):
        self.assertEqual(subtract_n_months(date(2010, 3, 31), 4),
                         date(2009, 11, 30))

    def testWithMoreThan12Months(self):
        self.assertEqual(subtract_n_months(date(2010, 3, 31), 25),
                         date(2008, 2, 29))
        self.assertEqual(subtract_n_months(date(2010, 3, 31), 37),
                         date(2007, 2, 28))
