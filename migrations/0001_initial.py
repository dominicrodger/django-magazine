# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Author'
        db.create_table('magazine_author', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('forename', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('surname', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('details', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
        ))
        db.send_create_signal('magazine', ['Author'])

        # Adding model 'Issue'
        db.create_table('magazine_issue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('issue_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('magazine', ['Issue'])

        # Adding model 'Article'
        db.create_table('magazine_article', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('subheading', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['magazine.Author'])),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('hits', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('allow_preview', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['magazine.Issue'])),
        ))
        db.send_create_signal('magazine', ['Article'])


    def backwards(self, orm):
        
        # Deleting model 'Author'
        db.delete_table('magazine_author')

        # Deleting model 'Issue'
        db.delete_table('magazine_issue')

        # Deleting model 'Article'
        db.delete_table('magazine_article')


    models = {
        'magazine.article': {
            'Meta': {'object_name': 'Article'},
            'allow_preview': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['magazine.Author']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'hits': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['magazine.Issue']"}),
            'subheading': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'magazine.author': {
            'Meta': {'ordering': "('surname', 'forename')", 'object_name': 'Author'},
            'details': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'forename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'magazine.issue': {
            'Meta': {'object_name': 'Issue'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue_date': ('django.db.models.fields.DateField', [], {}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['magazine']
