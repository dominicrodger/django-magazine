from datetime import date
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView
from django.views.generic import DetailView
from magazine.models import Article, Issue, Author, BookReview

class CurrentIssueListView(ListView):
    template_name = 'magazine/current_issue.html'
    context_object_name = 'current_articles'

    def get_current_issue(self):
        if not hasattr(self, 'current_issue'):
            self.current_issue = Issue.current_issue()

        return self.current_issue

    def get_context_data(self, **kwargs):
        context = super(CurrentIssueListView, self).get_context_data(**kwargs)
        context['current_issue'] = self.get_current_issue()
        context['book_reviews'] = BookReview.objects.filter(issue = self.get_current_issue())

        return context

    def get_queryset(self):
        if not self.get_current_issue():
            return Article.objects.none()

        return Article.objects.filter(issue = self.get_current_issue())

class IssueListView(ListView):
    template_name = 'magazine/issues.html'
    context_object_name = 'issues'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Issue.objects.all()

        return Issue.published_objects.all()

class IssueView(DetailView):
    template_name = 'magazine/issue_detail.html'
    context_object_name = 'issue'

    def get_context_data(self, **kwargs):
        context = super(IssueView, self).get_context_data(**kwargs)
        issue = self.get_object()
        context['articles'] = Article.objects.filter(issue = issue)
        context['book_reviews'] = BookReview.objects.filter(issue = issue)

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
        context = super(ArticleView, self).get_context_data(**kwargs)
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

class AuthorDetailView(DetailView):
    template_name = 'magazine/author_detail.html'
    context_object_name = 'author'

    def get_context_data(self, **kwargs):
        context = super(AuthorDetailView, self).get_context_data(**kwargs)
        author = self.get_object()
        qs = author.article_set.order_by('issue')

        if not self.request.user.is_staff:
            qs = qs.filter(issue__published = True, issue__issue_date__lte = date.today())

        context['num_articles'] = qs.count()
        context['articles'] = qs[:4]

        qs_reviews = author.bookreview_set.order_by('issue')
        if not self.request.user.is_staff:
            qs_reviews = qs_reviews.filter(issue__published = True, issue__issue_date__lte = date.today())

        context['num_book_reviews'] = qs_reviews.count()
        context['book_reviews'] = qs_reviews[:10]

        return context

    def get_queryset(self):
        return Author.objects.filter(indexable = True)

    def get_object(self, queryset = None):
        if not queryset:
            queryset = self.get_queryset()

        try:
            return queryset.get(pk = int(self.kwargs['pk']))
        except Author.DoesNotExist:
            raise Http404

class AuthorListView(ListView):
    template_name = 'magazine/authors.html'
    context_object_name = 'authors'
    paginate_by = 20

    def get_queryset(self):
        return Author.objects.order_by('-num_articles',).filter(num_articles__gt = 0, indexable = True)

class AuthorArticlesView(ListView):
    template_name = 'magazine/author_articles.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_author(self):
        if not hasattr(self, 'author'):
            self.author = Author.objects.get(pk = int(self.kwargs['pk']), indexable = True)

        return self.author

    def get_context_data(self, **kwargs):
        context = super(AuthorArticlesView, self).get_context_data(**kwargs)
        context['author'] = self.get_author()
        return context

    def get_queryset(self):
        return self.get_author().article_set.filter(issue__published = True, issue__issue_date__lte = date.today()).order_by('issue')

class AuthorBookReviewsView(ListView):
    template_name = 'magazine/author_book_reviews.html'
    context_object_name = 'book_reviews'
    paginate_by = 10

    def get_author(self):
        if not hasattr(self, 'author'):
            self.author = Author.objects.get(pk = int(self.kwargs['pk']), indexable = True)

        return self.author

    def get_context_data(self, **kwargs):
        context = super(AuthorBookReviewsView, self).get_context_data(**kwargs)
        context['author'] = self.get_author()
        return context

    def get_queryset(self):
        return self.get_author().bookreview_set.filter(issue__published = True, issue__issue_date__lte = date.today()).order_by('issue')

class BookReviewView(ArticleView):
    template_name = 'magazine/bookreview_detail.html'
    context_object_name = 'bookreview'

    def get_queryset(self):
        try:
            issue = Issue.objects.get(number = self.get_issue_number())

            if not issue.is_published() and not self.request.user.is_staff:
                return BookReview.objects.none()

            return BookReview.objects.filter(issue = issue)
        except Issue.DoesNotExist:
            return BookReview.objects.none()
