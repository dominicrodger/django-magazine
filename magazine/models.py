import calendar
import re
from datetime import date
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import F, Count
from django.utils.text import truncate_words
from django.template.defaultfilters import striptags
from sorl.thumbnail import ImageField, get_thumbnail
from magazine.utils.word_cleaner import clean_word_text

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

    def surname_forename(self):
        if self.surname:
            return u'{0}, {1}'.format(self.surname, self.forename)
        return self.forename
    surname_forename.short_description = u'Name'
    surname_forename.admin_order_field = 'surname'

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

class PublishedIssueManager(models.Manager):
    def get_query_set(self):
        return super(PublishedIssueManager, self).get_query_set().filter(issue_date__lte = date.today(), published = True).annotate(num_articles = Count('article'))

class IssueManager(models.Manager):
    def get_query_set(self):
        return super(IssueManager, self).get_query_set().annotate(num_articles = Count('article'))

class Issue(models.Model):
    number = models.PositiveIntegerField(help_text = u'The issue number.', unique = True)
    issue_date = models.DateField(help_text = u'The selected day is ignored - please use the first of the month')
    published = models.BooleanField(default = True, help_text = u'Uncheck to create an issue which is not yet published.')
    objects = IssueManager()
    published_objects = PublishedIssueManager()

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

heading_pattern = re.compile('<(/?)h(\d)>')

def increment_heading_tag(match):
    return '<{0}h{1}>'.format(match.group(1), int(match.group(2)) + 1)

class Article(models.Model):
    title = models.CharField(max_length = 250)
    subheading = models.CharField(max_length = 250, blank = True, null = True)
    authors = models.ManyToManyField(Author)
    description = models.TextField(blank = True, null = True, help_text = u'Introductory paragraph, if any.')
    text = models.TextField(blank = True, null = True, help_text = u'Full text of the article.')
    cleaned_text = models.TextField(blank = True, null = True, help_text = u'Auto-populated from the main body text, and cleaned up.')
    hits = models.IntegerField(default = 0)
    issue = models.ForeignKey(Issue)
    order_in_issue = models.PositiveIntegerField(default = 0)
    image = ImageField(upload_to = 'magazine', blank = True, null = True)

    objects = ArticleManager()
    objects_with_num_authors = ArticleManagerWithNumAuthors()

    def __unicode__(self):
        return self.title

    def mark_visited(self):
        Article.objects.filter(pk = self.pk).update(hits=F('hits') + 1)

    def all_authors(self):
        return self.authors.all()

    def admin_thumbnail(self):
        if not self.image:
            return u'(None)'
        im = get_thumbnail(self.image, '100x100', crop='center', quality=99)
        return u'<img src="{0}" />'.format(im.url)
    admin_thumbnail.short_description = 'Image'
    admin_thumbnail.allow_tags = True

    def save(self, *args, **kwargs):
        if self.text:
            self.cleaned_text = clean_word_text(self.text)
        return super(Article, self).save(*args, **kwargs)

    def teaser(self):
        if self.description:
            return self.description

        if self.cleaned_text:
            return truncate_words(striptags(self.cleaned_text), 50)

        return u'None available.'

    def demoted_text(self):
        return heading_pattern.sub(increment_heading_tag, self.cleaned_text)

    def get_absolute_url(self):
        return reverse('magazine_article_detail', args=[self.issue.number,self.pk,])

    class Meta:
        ordering = ('-issue', 'order_in_issue',)

class BookReviewManager(models.Manager):
    def get_query_set(self):
        return super(BookReviewManager, self).get_query_set().select_related(u'issue',)

class BookReview(models.Model):
    title = models.CharField(max_length = 250)
    authors = models.ManyToManyField(Author)
    text = models.TextField(blank = True, null = True, help_text = u'Full text of the review.')
    cleaned_text = models.TextField(blank = True, null = True, help_text = u'Auto-populated from the main body text, and cleaned up.')
    issue = models.ForeignKey(Issue)
    order_in_issue = models.PositiveIntegerField(default = 0)
    book_author = models.CharField(blank = True, null = True, max_length = 60)
    publisher = models.CharField(blank = True, null = True, max_length = 60)
    publisher_location = models.CharField(blank = True, null = True, max_length = 60)
    publication_date = models.CharField(max_length = 20, blank = True, null = True)
    num_pages = models.PositiveIntegerField(blank = True, null = True)
    price = models.CharField(blank = True, null = True, max_length = 250)
    isbn = models.CharField(blank = True, null = True, max_length = 20)
    hits = models.IntegerField(default = 0)

    objects = BookReviewManager()

    def __unicode__(self):
        if self.book_author:
            return u'{0} ({1})'.format(self.title, self.book_author)

        return self.title

    def mark_visited(self):
        BookReview.objects.filter(pk = self.pk).update(hits=F('hits') + 1)

    def all_authors(self):
        return self.authors.all()

    def save(self, *args, **kwargs):
        if self.text:
            self.cleaned_text = clean_word_text(self.text)
        return super(BookReview, self).save(*args, **kwargs)

    def teaser(self):
        if self.cleaned_text:
            return truncate_words(striptags(self.cleaned_text), 50)

        return u'None available.'

    def demoted_text(self):
        return heading_pattern.sub(increment_heading_tag, self.cleaned_text)

    def get_absolute_url(self):
        return reverse('magazine_bookreview_detail', args=[self.issue.number,self.pk,])

    class Meta:
        ordering = ('-issue', 'order_in_issue',)
