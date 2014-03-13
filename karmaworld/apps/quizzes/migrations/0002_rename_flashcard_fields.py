# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_column(u'quizzes_flashcardquestion', 'sideA', 'keyword_side')
        db.rename_column(u'quizzes_flashcardquestion', 'sideB', 'definition_side')


    def backwards(self, orm):
        db.rename_column(u'quizzes_flashcardquestion', 'keyword_side', 'sideA')
        db.rename_column(u'quizzes_flashcardquestion', 'definition_side', 'sideB')
