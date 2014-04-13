import json
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponse


def format_session_increment_field(cls, id, field):
    return cls.__name__ + '-' + field + '-' + str(id)


def ajax_base(request, event_processor, allowed_methods):
    """Handle an AJAX request"""
    if not request.method in allowed_methods or not request.is_ajax():
        # return that the api call failed
        return HttpResponseBadRequest(json.dumps({'status': 'fail', 'message': 'must be an ajax request with method ' + str(allowed_methods)}),
                                      mimetype="application/json")

    resp = event_processor(request)
    if resp:
        return resp
    else:
        return HttpResponse(status=204)


def ajax_pk_base(cls, request, pk, event_processor):
    """Handle an AJAX request"""
    if not request.is_ajax():
        # return that the api call failed
        return HttpResponseBadRequest(json.dumps({'status': 'fail', 'message': 'must be a POST ajax request'}),
                                      mimetype="application/json")

    try:
        obj = cls.objects.get(pk=pk)
        event_processor(request.user, obj)

    except ObjectDoesNotExist:
        return HttpResponseNotFound(json.dumps({'status': 'fail', 'message': 'id does not match a ' + cls.__name__}),
                                    mimetype="application/json")

    return HttpResponse(status=204)


def ajax_increment(cls, request, pk, field, user_profile_field=None, event_processor=None):
    def ajax_increment_work(request_user, obj):
        count = getattr(obj, field)
        setattr(obj, field,  count+1)
        obj.save()

        if event_processor:
            event_processor(request.user, obj)

        # Record that user has performed this, to prevent
        # them from doing it again
        if user_profile_field:
            getattr(request_user.get_profile(), user_profile_field).add(obj)
            obj.save()

    return ajax_pk_base(cls, request, pk, ajax_increment_work)
