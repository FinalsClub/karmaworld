# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'License', fields ['name']
        db.create_unique('licenses_license', ['name'])


    def backwards(self, orm):
        # Removing unique constraint on 'License', fields ['name']
        db.delete_unique('licenses_license', ['name'])


    models = {
        'licenses.license': {
            'Meta': {'object_name': 'License'},
            'html': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'})
        }
    }

    complete_apps = ['licenses']