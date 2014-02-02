# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding M2M table for field thanked_notes on 'UserProfile'
        m2m_table_name = db.shorten_name(u'users_userprofile_thanked_notes')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm[u'users.userprofile'], null=False)),
            ('note', models.ForeignKey(orm[u'notes.note'], null=False))
        ))
        db.create_unique(m2m_table_name, ['userprofile_id', 'note_id'])

        # Adding M2M table for field flagged_notes on 'UserProfile'
        m2m_table_name = db.shorten_name(u'users_userprofile_flagged_notes')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm[u'users.userprofile'], null=False)),
            ('note', models.ForeignKey(orm[u'notes.note'], null=False))
        ))
        db.create_unique(m2m_table_name, ['userprofile_id', 'note_id'])

        # Adding M2M table for field flagged_courses on 'UserProfile'
        m2m_table_name = db.shorten_name(u'users_userprofile_flagged_courses')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm[u'users.userprofile'], null=False)),
            ('course', models.ForeignKey(orm[u'courses.course'], null=False))
        ))
        db.create_unique(m2m_table_name, ['userprofile_id', 'course_id'])


    def backwards(self, orm):
        # Removing M2M table for field thanked_notes on 'UserProfile'
        db.delete_table(db.shorten_name(u'users_userprofile_thanked_notes'))

        # Removing M2M table for field flagged_notes on 'UserProfile'
        db.delete_table(db.shorten_name(u'users_userprofile_flagged_notes'))

        # Removing M2M table for field flagged_courses on 'UserProfile'
        db.delete_table(db.shorten_name(u'users_userprofile_flagged_courses'))


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'courses.course': {
            'Meta': {'ordering': "['-file_count', 'school', 'name']", 'unique_together': "(('name', 'department'),)", 'object_name': 'Course'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'department': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['courses.Department']", 'null': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.TextField', [], {'max_length': '511', 'null': 'True', 'blank': 'True'}),
            'file_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'flags': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructor_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'instructor_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
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
        },
        u'licenses.license': {
            'Meta': {'object_name': 'License'},
            'html': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'})
        },
        u'notes.note': {
            'Meta': {'ordering': "['-uploaded_at']", 'unique_together': "(('fp_file', 'upstream_link'),)", 'object_name': 'Note'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['courses.Course']"}),
            'file_type': ('django.db.models.fields.CharField', [], {'default': "'???'", 'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'flags': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fp_file': ('django_filepicker.models.FPFileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'gdrive_url': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'is_hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'license': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['licenses.License']", 'null': 'True', 'blank': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'pdf_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'static_html': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'thanks': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'tweeted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow', 'null': 'True'}),
            'upstream_link': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'default': '2014', 'null': 'True', 'blank': 'True'})
        },
        u'taggit.tag': {
            'Meta': {'ordering': "['namespace', 'name']", 'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'namespace': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_tagged_items'", 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_items'", 'to': u"orm['taggit.Tag']"})
        },
        u'users.coursekarmaevent': {
            'Meta': {'unique_together': "(('points', 'user', 'timestamp'),)", 'object_name': 'CourseKarmaEvent'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['courses.Course']"}),
            'event_type': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'points': ('django.db.models.fields.IntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'users.generickarmaevent': {
            'Meta': {'unique_together': "(('points', 'user', 'timestamp'),)", 'object_name': 'GenericKarmaEvent'},
            'event_type': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '15'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'points': ('django.db.models.fields.IntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'users.notekarmaevent': {
            'Meta': {'unique_together': "(('points', 'user', 'timestamp'),)", 'object_name': 'NoteKarmaEvent'},
            'event_type': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['notes.Note']"}),
            'points': ('django.db.models.fields.IntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'users.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'flagged_courses': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'users_flagged'", 'symmetrical': 'False', 'to': u"orm['courses.Course']"}),
            'flagged_notes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'users_flagged'", 'symmetrical': 'False', 'to': u"orm['notes.Note']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['courses.School']", 'null': 'True', 'blank': 'True'}),
            'thanked_notes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'users_thanked'", 'symmetrical': 'False', 'to': u"orm['notes.Note']"}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['users']