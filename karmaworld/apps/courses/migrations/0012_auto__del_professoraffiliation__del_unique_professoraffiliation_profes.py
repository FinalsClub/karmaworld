# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Course', fields ['name', 'department']
        db.delete_unique(u'courses_course', ['name', 'department_id'])

        # Removing unique constraint on 'ProfessorTaught', fields ['professor', 'course']
        db.delete_unique(u'courses_professortaught', ['professor_id', 'course_id'])

        # Removing unique constraint on 'ProfessorAffiliation', fields ['professor', 'department']
        db.delete_unique(u'courses_professoraffiliation', ['professor_id', 'department_id'])

        # Deleting model 'ProfessorAffiliation'
        db.delete_table(u'courses_professoraffiliation')

        # Deleting model 'ProfessorTaught'
        db.delete_table(u'courses_professortaught')

        # Adding M2M table for field professor on 'Course'
        m2m_table_name = db.shorten_name(u'courses_course_professor')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm[u'courses.course'], null=False)),
            ('professor', models.ForeignKey(orm[u'courses.professor'], null=False))
        ))
        db.create_unique(m2m_table_name, ['course_id', 'professor_id'])

        # Adding unique constraint on 'Course', fields ['name', 'school']
        db.create_unique(u'courses_course', ['name', 'school_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Course', fields ['name', 'school']
        db.delete_unique(u'courses_course', ['name', 'school_id'])

        # Adding model 'ProfessorAffiliation'
        db.create_table(u'courses_professoraffiliation', (
            ('department', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['courses.Department'])),
            ('professor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['courses.Professor'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'courses', ['ProfessorAffiliation'])

        # Adding unique constraint on 'ProfessorAffiliation', fields ['professor', 'department']
        db.create_unique(u'courses_professoraffiliation', ['professor_id', 'department_id'])

        # Adding model 'ProfessorTaught'
        db.create_table(u'courses_professortaught', (
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['courses.Course'])),
            ('professor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['courses.Professor'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'courses', ['ProfessorTaught'])

        # Adding unique constraint on 'ProfessorTaught', fields ['professor', 'course']
        db.create_unique(u'courses_professortaught', ['professor_id', 'course_id'])

        # Removing M2M table for field professor on 'Course'
        db.delete_table(db.shorten_name(u'courses_course_professor'))

        # Adding unique constraint on 'Course', fields ['name', 'department']
        db.create_unique(u'courses_course', ['name', 'department_id'])


    models = {
        u'courses.course': {
            'Meta': {'ordering': "['-file_count', 'school', 'name']", 'unique_together': "(('name', 'school'),)", 'object_name': 'Course'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'department': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['courses.Department']", 'null': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.TextField', [], {'max_length': '511', 'null': 'True', 'blank': 'True'}),
            'file_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'flags': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructor_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'instructor_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'professor': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['courses.Professor']", 'null': 'True', 'blank': 'True'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['courses.School']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '150', 'null': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '511', 'null': 'True', 'blank': 'True'})
        },
        u'courses.department': {
            'Meta': {'unique_together': "(('name', 'school'),)", 'object_name': 'Department'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['courses.School']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '150', 'null': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '511', 'null': 'True', 'blank': 'True'})
        },
        u'courses.professor': {
            'Meta': {'unique_together': "(('name', 'email'),)", 'object_name': 'Professor'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'courses.school': {
            'Meta': {'ordering': "['-file_count', '-priority', 'name']", 'object_name': 'School'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'file_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'hashtag': ('django.db.models.fields.CharField', [], {'max_length': '16', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'priority': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '150', 'null': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '511', 'blank': 'True'}),
            'usde_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['courses']