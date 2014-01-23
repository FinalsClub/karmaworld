import json
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponse


def format_session_increment_field(cls, id, field):
    return cls.__name__ + '-' + field + '-' + str(id)


def ajax_increment(cls, request, pk, field, event_processor=None):
    """Increment a note's field by one."""
    if not (request.method == 'POST' and request.is_ajax()):
        # return that the api call failed
        return HttpResponseBadRequest(json.dumps({'status': 'fail', 'message': 'must be a POST ajax request'}),
                                      mimetype="application/json")

    try:
        # Increment counter
        note = cls.objects.get(pk=pk)
        count = getattr(note, field)
        setattr(note, field,  count+1)
        note.save()

        if event_processor:
            event_processor(request.user, note)

        # Record that user has performed this, to prevent
        # them from doing it again
        request.session[format_session_increment_field(cls, pk, field)] = True
    except ObjectDoesNotExist:
        return HttpResponseNotFound(json.dumps({'status': 'fail', 'message': 'note id does not match a note'}),
                                    mimetype="application/json")

    return HttpResponse(status=204)

