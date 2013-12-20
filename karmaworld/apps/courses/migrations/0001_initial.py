# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'School'
        db.create_table('courses_school', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=150, null=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=511, blank=True)),
            ('facebook_id', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('usde_id', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('file_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('priority', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('courses', ['School'])

        # Adding model 'Course'
        db.create_table('courses_course', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=150, null=True)),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['courses.School'])),
            ('file_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('desc', self.gf('django.db.models.fields.TextField')(max_length=511, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=511, null=True, blank=True)),
            ('academic_year', self.gf('django.db.models.fields.IntegerField')(default=2013, null=True, blank=True)),
            ('instructor_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('instructor_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.utcnow)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('courses', ['Course'])


    def backwards(self, orm):
        # Deleting model 'School'
        db.delete_table('courses_school')

        # Deleting model 'Course'
        db.delete_table('courses_course')


    models = {
        'courses.course': {
            'Meta': {'ordering': "['-file_count', 'school', 'name']", 'object_name': 'Course'},
            'academic_year': ('django.db.models.fields.IntegerField', [], {'default': '2013', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.TextField', [], {'max_length': '511', 'null': 'True', 'blank': 'True'}),
            'file_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructor_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'instructor_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.School']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '150', 'null': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '511', 'null': 'True', 'blank': 'True'})
        },
        'courses.school': {
            'Meta': {'ordering': "['-file_count', '-priority', 'name']", 'object_name': 'School'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'file_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'priority': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '150', 'null': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '511', 'blank': 'True'}),
            'usde_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['courses']