from django.contrib import admin
from magazine.models import Author, Article, Issue

try:
    from tinymce.widgets import TinyMCE
    HAS_TINYMCE = True
except ImportError:
    HAS_TINYMCE = False

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('forename', 'surname',)
    search_fields = ('forename', 'surname',)
admin.site.register(Author, AuthorAdmin)

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'hits', 'issue',)
    search_fields = ('title', 'subheading', 'description', 'text',)
    readonly_fields = ('hits',)
    filter_horizontal = ('authors',)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if HAS_TINYMCE and db_field.name in ('text',):
            return db_field.formfield(widget=TinyMCE(
                attrs={'cols': 80, 'rows': 30},
            ))
        return super(ArticleAdmin, self).formfield_for_dbfield(db_field, **kwargs)

admin.site.register(Article, ArticleAdmin)

class IssueAdmin(admin.ModelAdmin):
    list_display = ('number', 'month_year', 'published',)
    list_filter = ('published',)
admin.site.register(Issue, IssueAdmin)
