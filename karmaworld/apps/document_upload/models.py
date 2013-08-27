import datetime

from django.db import models

import django_filepicker

class IntakeDoc(models.Model):
    fp_note = django_filepicker.models.FPFileField(upload_to='queue/%Y/%m/%j/',
                help_text=u"An uploaded file reference from Filepicker.io")
    form    = models.TextField(max_length=1024,
                help_text=u"A serilized version of the note data form")
    ip      = models.IPAddressField(blank=True, null=True,
                help_text=u"IP address of the uploader")

    uploaded_at     = models.DateTimeField(null=True, default=datetime.datetime.utcnow)

    class Meta:
        """ Sort files most recent first """
        ordering = ['-uploaded_at']


    def __unicode__(self):
        return u"{0} @ {1}".format(self.ip, self.uploaded_at)

    def convert_to_note(self):
        """ polymorph this object into a note.models.Note object  """
        pass
