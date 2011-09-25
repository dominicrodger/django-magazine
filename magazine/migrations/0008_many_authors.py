# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Article.author'
        db.delete_column('magazine_article', 'author_id')

        # Adding M2M table for field authors on 'Article'
        db.create_table('magazine_article_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('article', models.ForeignKey(orm['magazine.article'], null=False)),
            ('author', models.ForeignKey(orm['magazine.author'], null=False))
        ))
        db.create_unique('magazine_article_authors', ['article_id', 'author_id'])


    def backwards(self, orm):
        
        # We cannot add back in field 'Article.author'
        raise RuntimeError(
            "Cannot reverse this migration. 'Article.author' and its values cannot be restored.")

        # Removing M2M table for field authors on 'Article'
        db.delete_table('magazine_article_authors')


    models = {
        'magazine.article': {
            'Meta': {'ordering': "('-issue', 'order_in_issue')", 'object_name': 'Article'},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['magazine.Author']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'hits': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['magazine.Issue']"}),
            'order_in_issue': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'subheading': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'magazine.author': {
            'Meta': {'ordering': "('surname', 'forename')", 'object_name': 'Author'},
            'details': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'forename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'magazine.issue': {
            'Meta': {'ordering': "('-issue_date',)", 'object_name': 'Issue'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue_date': ('django.db.models.fields.DateField', [], {}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        }
    }

    complete_apps = ['magazine']
