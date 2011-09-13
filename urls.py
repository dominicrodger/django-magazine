from django.conf.urls.defaults import *
from magazine.models import Article
from magazine.views import CurrentIssueListView, IssueView, ArticleView

urlpatterns = patterns('',
    url(r'^$', CurrentIssueListView.as_view(), name='magazine_index'),
    url(r'^(?P<number>([0-9]+))/$', IssueView.as_view(), name='issue_detail'),
    url(r'^(?P<number>([0-9]+))/(?P<pk>([0-9]+))/$', ArticleView.as_view(), name='article_detail'),
)