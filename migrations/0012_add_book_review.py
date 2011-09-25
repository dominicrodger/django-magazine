# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'BookReview'
        db.create_table('magazine_bookreview', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('cleaned_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['magazine.Issue'])),
            ('order_in_issue', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('book_author', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('publisher', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('publisher_location', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('publication_date', self.gf('django.db.models.fields.CharField')(max_length=20,null=True, blank=True)),
            ('num_pages', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('price', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('isbn', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('hits', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('magazine', ['BookReview'])

        # Adding M2M table for field authors on 'BookReview'
        db.create_table('magazine_bookreview_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('bookreview', models.ForeignKey(orm['magazine.bookreview'], null=False)),
            ('author', models.ForeignKey(orm['magazine.author'], null=False))
        ))
        db.create_unique('magazine_bookreview_authors', ['bookreview_id', 'author_id'])


    def backwards(self, orm):
        
        # Deleting model 'BookReview'
        db.delete_table('magazine_bookreview')

        # Removing M2M table for field authors on 'BookReview'
        db.delete_table('magazine_bookreview_authors')


    models = {
        'magazine.article': {
            'Meta': {'ordering': "('-issue', 'order_in_issue')", 'object_name': 'Article'},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['magazine.Author']", 'symmetrical': 'False'}),
            'cleaned_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
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
            'indexable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'magazine.bookreview': {
            'Meta': {'ordering': "('-issue', 'order_in_issue')", 'object_name': 'BookReview'},
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
            'Meta': {'ordering': "('-issue_date',)", 'object_name': 'Issue'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue_date': ('django.db.models.fields.DateField', [], {}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        }
    }

    complete_apps = ['magazine']
