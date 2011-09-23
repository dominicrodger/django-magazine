from django.contrib import admin
from magazine.models import Author, Article, Issue

try:
    from tinymce.widgets import TinyMCE
    HAS_TINYMCE = True
except ImportError:
    HAS_TINYMCE = False

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('surname_forename', 'get_num_articles', 'indexable',)
    search_fields = ('forename', 'surname',)
    list_filter = ('indexable',)
    actions = ['make_nonindexable', 'make_indexable',]

    def make_nonindexable(modeladmin, request, queryset):
        queryset.update(indexable=False)
    make_nonindexable.short_description = "Mark selected authors as non-indexable"

    def make_indexable(modeladmin, request, queryset):
        queryset.update(indexable=True)
    make_indexable.short_description = "Mark selected authors as indexable"

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
