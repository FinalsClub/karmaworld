#!/usr/bin/env python2
from django.core.management import BaseCommand

import nltk


class Command(BaseCommand):
    help = "Download the data needed for the Natural Language Toolkit to find note keywords."

    def handle(self, *args, **kwargs):
        nltk.download('punkt')
        nltk.download('maxent_treebank_pos_tagger')
        nltk.download('stopwords')

