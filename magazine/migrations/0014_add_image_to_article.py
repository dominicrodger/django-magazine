# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding field 'Article.image'
        db.add_column('magazine_article', 'image', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100, null=True, blank=True), keep_default=False)
    
    
    def backwards(self, orm):
        
        # Deleting field 'Article.image'
        db.delete_column('magazine_article', 'image')
    
    
    models = {
        'magazine.article': {
            'Meta': {'object_name': 'Article'},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['magazine.Author']", 'symmetrical': 'False'}),
            'cleaned_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'hits': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['magazine.Issue']"}),
            'order_in_issue': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'subheading': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'magazine.author': {
            'Meta': {'object_name': 'Author'},
            'details': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'forename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indexable': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'magazine.bookreview': {
            'Meta': {'object_name': 'BookReview'},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['magazine.Author']", 'symmetrical': 'False'}),
            'book_author': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'cleaned_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'hits': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isbn': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['magazine.Issue']"}),
            'num_pages': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'order_in_issue': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'price': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'publication_date': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'publisher': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'publisher_location': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'magazine.issue': {
            'Meta': {'object_name': 'Issue'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue_date': ('django.db.models.fields.DateField', [], {}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['magazine']
