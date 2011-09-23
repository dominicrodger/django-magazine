import calendar
from datetime import date
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import F, Count
from django.utils.text import truncate_words
from django.template.defaultfilters import striptags

EMBARGO_TIME_IN_MONTHS = int(getattr(settings, 'MAGAZINE_EMBARGO_TIME_IN_MONTHS', 2))

class AuthorManager(models.Manager):
    def get_query_set(self):
        return super(AuthorManager, self).get_query_set().annotate(num_articles = Count('article'))

class Author(models.Model):
    forename = models.CharField(max_length = 100, help_text = u'The author\'s forename')
    surname = models.CharField(blank = True, null = True, max_length = 100, help_text = u'The author\'s surname')
    details = models.TextField(blank = True, null = True, help_text = u'Details about the author')
    indexable = models.BooleanField(default = True, help_text = u'Select this for authors who shouldn\'t have their own page (e.g. "Anonymous")')

    objects = AuthorManager()

    def __unicode__(self):
        if self.surname:
            return u'{0} {1}'.format(self.forename, self.surname)

        return self.forename

    def get_absolute_url(self):
        if not self.indexable:
            # This is going to be a problem, but there's not really a lot we can do here.
            pass
        return reverse('magazine_author_detail', args=[self.pk,])

    def get_num_articles(self):
        if not hasattr(self, 'num_articles'):
            self.num_articles = self.article_set.count()

        return self.num_articles
    get_num_articles.short_description = u'Articles'
    get_num_articles.admin_order_field = 'num_articles'

    class Meta:
        ordering = ('surname', 'forename',)

class PublishedIssueManager(models.Manager):
    def get_query_set(self):
        return super(PublishedIssueManager, self).get_query_set().filter(issue_date__lte = date.today(), published = True)

def __days_in_month(year, month):
    d = date(year, month, 1)

    return calendar.monthrange(year, month)[1]

def subtract_n_months(date_val, num_months):
    # Split the number of months to subtract into months and years
    year, month = divmod(num_months, 12)

    if date_val.month <= month:
        year = date_val.year - year - 1
        month = date_val.month - month + 12
    else:
        year = date_val.year - year
        month = date_val.month - month

    try:
        return date(year, month, date_val.day)
    except ValueError:
        return date(year, month, __days_in_month(year, month))

class Issue(models.Model):
    number = models.PositiveIntegerField(help_text = u'The issue number.', unique = True)
    issue_date = models.DateField(help_text = u'The selected day is ignored - please use the first of the month')
    published = models.BooleanField(default = True, help_text = u'Uncheck to create an issue which is not yet published.')
    published_objects = PublishedIssueManager()
    objects = models.Manager()

    def __unicode__(self):
        return u'Issue {0}'.format(self.number)

    def save(self, *args, **kwargs):
        self.issue_date = self.issue_date.replace(day = 1)
        super(Issue, self).save(*args, **kwargs)

    def month_year(self):
        return self.issue_date.strftime(u'%B %Y')
    month_year.admin_order_field = 'issue_date'
    month_year.short_description = 'Issue date'

    def is_published(self):
        return self.issue_date <= date.today() and self.published

    def embargoed(self):
        if not self.is_published():
            return True

        today = date.today()

        # Figure out if it's at least EMBARGO_TIME_IN_MONTHS old
        if subtract_n_months(today, EMBARGO_TIME_IN_MONTHS) < self.issue_date:
            return True

        return False

    def get_absolute_url(self):
        return reverse('magazine_issue_detail', args=[self.number,])

    @staticmethod
    def current_issue():
        live_issues = Issue.published_objects.all()

        if not live_issues:
            return None

        return live_issues[0]

    class Meta:
        ordering = ('-issue_date',)

class ArticleManager(models.Manager):
    def get_query_set(self):
        return super(ArticleManager, self).get_query_set().select_related(u'issue',)

class ArticleManagerWithNumAuthors(ArticleManager):
    def get_query_set(self):
        return super(ArticleManagerWithNumAuthors, self).get_query_set().annotate(num_authors = Count('authors'))

class Article(models.Model):
    title = models.CharField(max_length = 250)
    subheading = models.CharField(max_length = 250, blank = True, null = True)
    authors = models.ManyToManyField(Author)
    description = models.TextField(blank = True, null = True, help_text = u'Introductory paragraph, if any.')
    text = models.TextField(blank = True, null = True, help_text = u'Full text of the article.')
    hits = models.IntegerField(default = 0)
    issue = models.ForeignKey(Issue)
    order_in_issue = models.PositiveIntegerField(default = 0)

    objects = ArticleManager()
    objects_with_num_authors = ArticleManagerWithNumAuthors()

    def __unicode__(self):
        return self.title

    def mark_visited(self):
        Article.objects.filter(pk = self.pk).update(hits=F('hits') + 1)

    def teaser(self):
        if self.description:
            return self.description

        if self.text:
            return truncate_words(striptags(self.text), 50)

        return u'None available.'

    def get_absolute_url(self):
        return reverse('magazine_article_detail', args=[self.issue.number,self.pk,])

    class Meta:
        ordering = ('-issue', 'order_in_issue',)
