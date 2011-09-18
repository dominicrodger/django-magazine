from django.contrib import admin
from magazine.models import Author, Article, Issue

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('forename', 'surname',)
    search_fields = ('forename', 'surname',)
admin.site.register(Author, AuthorAdmin)

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'hits', 'issue',)
    search_fields = ('title', 'subheading', 'description', 'text',)
    readonly_fields = ('hits',)
admin.site.register(Article, ArticleAdmin)

class IssueAdmin(admin.ModelAdmin):
    list_display = ('number', 'month_year', 'published',)
    list_filter = ('published',)
admin.site.register(Issue, IssueAdmin)
