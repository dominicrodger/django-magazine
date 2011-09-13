from datetime import date
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import F
from django.utils.text import truncate_words

class Author(models.Model):
    forename = models.CharField(max_length = 100, help_text = u'The author\'s forename')
    surname = models.CharField(max_length = 100, help_text = u'The author\'s surname')
    details = models.TextField(blank = True, null = True, help_text = u'Details about the author')

    def __unicode__(self):
        return u'{0} {1}'.format(self.forename, self.surname)

    class Meta:
        ordering = ('surname', 'forename',)

class PublishedIssueManager(models.Manager):
    def get_query_set(self):
        return super(PublishedIssueManager, self).get_query_set().filter(issue_date__lte = date.today(), published = True)

class Issue(models.Model):
    number = models.PositiveIntegerField(help_text = u'The issue number.', unique = True)
    issue_date = models.DateField(help_text = u'The selected day is ignored - please use the first of the month')
    published = models.BooleanField(default = True, help_text = u'Uncheck to create an issue which is not yet published.')
    published_objects = PublishedIssueManager()
    objects = models.Manager()

    def __unicode__(self):
        return u'Issue {0}'.format(self.number)

    def month_year(self):
        return self.issue_date.strftime(u'%B %Y')
    month_year.admin_order_field = 'issue_date'
    month_year.short_description = 'Issue date'

    def is_published(self):
        return self.issue_date <= date.today() and self.published

    def get_absolute_url(self):
        return reverse('issue_detail', args=[self.number,])

    @staticmethod
    def current_issue():
        live_issues = Issue.published_objects.all()

        if not live_issues:
            return None

        return live_issues[0]

    class Meta:
        ordering = ('-issue_date',)

class Article(models.Model):
    title = models.CharField(max_length = 250)
    subheading = models.CharField(max_length = 250, blank = True, null = True)
    author = models.ForeignKey(Author)
    description = models.TextField(blank = True, null = True, help_text = u'Introductory paragraph, if any.')
    text = models.TextField(blank = True, null = True, help_text = u'Full text of the article.')
    hits = models.IntegerField(default = 0)
    issue = models.ForeignKey(Issue)
    order_in_issue = models.PositiveIntegerField(default = 0)

    def __unicode__(self):
        return self.title

    def mark_visited(self):
        Article.objects.filter(pk = self.pk).update(hits=F('hits') + 1)

    def teaser(self):
        if self.description:
            return self.description

        if self.text:
            return truncate_words(self.text, 50)

        return u'None available.'

    def get_absolute_url(self):
        return reverse('article_detail', args=[self.issue.number,self.pk,])

    class Meta:
        ordering = ('-issue', 'order_in_issue',)