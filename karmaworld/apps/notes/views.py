from django.views.generic import DetailView
from karmaworld.apps.notes.models import Note

class NoteDetailView(DetailView):
    """ Class-based view for the note html page """

    # name passed to template
    context_object_name = u"note"
    model = Note
