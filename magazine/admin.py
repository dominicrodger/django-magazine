from django.contrib import admin
from magazine.models import Author, Article, Issue, BookReview
from tinymce.widgets import TinyMCE
from sorl.thumbnail.admin import AdminImageMixin


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('surname_forename', 'get_num_articles', 'indexable',)
    search_fields = ('forename', 'surname',)
    list_filter = ('indexable',)
    actions = ['make_nonindexable', 'make_indexable', ]

    def make_nonindexable(modeladmin, request, queryset):
        queryset.update(indexable=False)
    make_nonindexable.short_description = "Mark selected authors "
    "as non-indexable"

    def make_indexable(modeladmin, request, queryset):
        queryset.update(indexable=True)
    make_indexable.short_description = "Mark selected authors as indexable"

admin.site.register(Author, AuthorAdmin)


class ArticleAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('title', 'admin_thumbnail', 'hits', 'issue', 'updated',)
    search_fields = ('title', 'subheading', 'description', 'text',)
    readonly_fields = ('hits',)
    filter_horizontal = ('authors',)
    exclude = ('cleaned_text',)
    ordering = ('issue',)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ('text',):
            return db_field.formfield(widget=TinyMCE(
                attrs={'cols': 80, 'rows': 30},
            ))
        return super(ArticleAdmin, self).\
            formfield_for_dbfield(db_field, **kwargs)

admin.site.register(Article, ArticleAdmin)


class IssueAdmin(admin.ModelAdmin):
    list_display = ('number', 'month_year', 'published',)
    list_filter = ('published',)
admin.site.register(Issue, IssueAdmin)


class BookReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'hits', 'issue', 'book_author', 'updated',)
    search_fields = ('title', 'book_author', 'text',)
    readonly_fields = ('hits',)
    filter_horizontal = ('authors',)
    exclude = ('cleaned_text',)
    ordering = ('issue',)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ('text',):
            return db_field.formfield(widget=TinyMCE(
                attrs={'cols': 80, 'rows': 30},
            ))
        return super(BookReviewAdmin, self).\
            formfield_for_dbfield(db_field, **kwargs)

admin.site.register(BookReview, BookReviewAdmin)
