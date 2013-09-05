# flake8: noqa

from magazine.tests.articles import ArticleTestCase
from magazine.tests.authors import AuthorTestCase
from magazine.tests.filters import (
    MagazineFiltersTestCase,
    MagazineTagsTestCase)
from magazine.tests.html_sanitizer import HTMLSanitizerTestCase
from magazine.tests.issues import IssueTestCase, NoIssuesTestCase
from magazine.tests.utils import SubtractNMonthsTestCase
from magazine.tests.views import MagazineGeneralViewsTestCase
