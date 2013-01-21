from io import FileIO, BufferedWriter
import os

from django.conf import settings

from ajaxuploader.backends.base import AbstractUploadBackend
from karmaworld.apps.notes import tasks
from karmaworld.apps.notes.models import Note

class LocalUploadBackend(AbstractUploadBackend):
    #UPLOAD_DIR = "uploads"
    # The below key must be synchronized with the implementing project
    # Used to store an array of unclaimed file_pks in the django session
    # So they can be claimed later when the anon user authenticates
    #SESSION_UNCLAIMED_FILES_KEY = KarmaSettings.SESSION_UNCLAIMED_FILES_KEY

    # When a file is uploaded anonymously, 
    # What username should we assign ownership to?
    # This is important because File.save
    # behavior will not set awarded_karma to True 
    # until an owner is assigned who has username != this
    #DEFAULT_UPLOADER_USERNAME = KarmaSettings.DEFAULT_UPLOADER_USERNAME

    def setup(self, filename):
        self._path = os.path.join(
            settings.MEDIA_ROOT, filename)
        try:
            os.makedirs(os.path.realpath(os.path.dirname(self._path)))
        except:
            pass
        self._dest = BufferedWriter(FileIO(self._path, "w"))

    def upload_chunk(self, chunk):
        self._dest.write(chunk)

    def upload(self, uploaded, filename, raw_data):
        try:
            if raw_data:
                # File was uploaded via ajax, and is streaming in.
                chunk = uploaded.read(self.BUFFER_SIZE)
                while len(chunk) > 0:
                    self.upload_chunk(chunk)
                    chunk = uploaded.read(self.BUFFER_SIZE)
            else:
                # File was uploaded via a POST, and is here.
                for chunk in uploaded.chunks():
                    self.upload_chunk(chunk)
            return True
        except:
            # things went badly.
            return False

    def upload_complete(self, request, filename, upload):
        path = settings.MEDIA_URL + "/" + filename
        self._dest.close()

        self._dir = settings.MEDIA_ROOT

        # Avoid File.objects.create, as this will try to make
        # Another file copy at FileField's 'upload_to' dir
        note = Note()
        note.note_file = os.path.join(self._dir, filename)
        note.save()

        # FIXME: Make get or create
        if self.SESSION_UNCLAIMED_FILES_KEY in request.session:
            request.session['uploaded_files'].append(note.pk)
        else:
            request.session['uploaded_files'] = [note.pk]

        # Asynchronously process document with Google Documents API
        print "upload_complete, firing task"
        tasks.process_document.delay(new_File)

        return {"path": path, "file_pk": note.pk}

    def update_filename(self, request, filename):
        """
        Returns a new name for the file being uploaded.
        Ensure file with name doesn't exist, and if it does,
        create a unique filename to avoid overwriting
        """
        self._dir = settings.MEDIA_ROOT
        unique_filename = False
        filename_suffix = 0

        #print "orig filename: " + os.path.join(self._dir, filename)

        # Check if file at filename exists
        if os.path.isfile(os.path.join(self._dir, filename)):
            while not unique_filename:
                try:
                    if filename_suffix == 0:
                        open(os.path.join(self._dir, filename))
                    else:
                        filename_no_extension, extension = os.path.splitext(filename)
                        #print "filename all ready exists. Trying  " + filename_no_extension + str(filename_suffix) + extension
                        open(os.path.join(self._dir, filename_no_extension + str(filename_suffix) + extension))
                    filename_suffix += 1
                except IOError:
                    unique_filename = True

        if filename_suffix == 0:
            #print "using filename: " + os.path.join(self._dir, filename)
            return filename
        else:
            #print "using filename: " + filename_no_extension + str(filename_suffix) + extension
            return filename_no_extension + str(filename_suffix) + extension

