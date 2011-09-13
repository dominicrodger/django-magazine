from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView
from django.views.generic import DetailView
from magazine.models import Article, Issue

class CurrentIssueListView(ListView):
    template_name = 'magazine/current_issue.html'
    context_object_name = 'current_articles'

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['current_issue'] = Issue.current_issue()
        return context

    def get_queryset(self):
        live_issue = Issue.current_issue()

        if not live_issue:
            return Article.objects.none()

        return Article.objects.filter(issue = live_issue)

class IssueView(DetailView):
    template_name = 'magazine/issue_detail.html'
    context_object_name = 'issue'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        issue = self.get_object()
        context['articles'] = Article.objects.filter(issue = issue)
        return context
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Issue.objects.all()

        return Issue.published_objects.all()

    def get_object(self, queryset = None):
        if not queryset:
            queryset = self.get_queryset()

        try:
            return queryset.get(number = int(self.kwargs['number']))
        except Issue.DoesNotExist:
            raise Http404

class ArticleView(DetailView):
    template_name = 'magazine/article_detail.html'
    context_object_name = 'article'

    def get_issue_number(self):
        return int(self.kwargs['number'])

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['issue'] = Issue.objects.get(number = self.get_issue_number())
        return context

    def get_queryset(self):
        try:
            issue = Issue.objects.get(number = self.get_issue_number())

            if not issue.is_published() and not self.request.user.is_staff:
                return Article.objects.none()

            return Article.objects.filter(issue = issue)
        except Issue.DoesNotExist:
            return Article.objects.none()

    def get_object(self, queryset = None):
        if not queryset:
            queryset = self.get_queryset()

        try:
            obj = queryset.get(pk = int(self.kwargs['pk']))
            obj.mark_visited()
            return obj
        except Article.DoesNotExist:
            raise Http404