from django.conf.urls.defaults import *
from magazine.models import Article
from magazine.views import CurrentIssueListView, IssueView, ArticleView, AuthorDetailView

urlpatterns = patterns('',
    url(r'^$', CurrentIssueListView.as_view(), name='magazine_index'),
    url(r'^issues/(?P<number>([0-9]+))/$', IssueView.as_view(), name='issue_detail'),
    url(r'^issues/(?P<number>([0-9]+))/(?P<pk>([0-9]+))/$', ArticleView.as_view(), name='article_detail'),
    url(r'^authors/(?P<pk>([0-9]+))/$', AuthorDetailView.as_view(), name='author_detail'),
)