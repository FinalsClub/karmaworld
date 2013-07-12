from django.utils import simplejson as json
from django.core.serializers.json import DjangoJSONEncoder

from django.http import HttpResponse, HttpResponseBadRequest, Http404

from ajaxuploader.backends.local import LocalUploadBackend

class AjaxFileUploader(object):
    def __init__(self, backend=None, **kwargs):
        if backend is None:
            backend = LocalUploadBackend
        self.get_backend = lambda: backend(**kwargs)

    def __call__(self,request):
        """ Make the resulting AjaxFileUploader instance itself a callable object """
        return self._ajax_upload(request)

    def _ajax_upload(self, request):
        #FIXME: `upload` is two possible types based on upload type

        if request.method == "POST":
            if request.is_ajax():
                # This case is for:
                # + async ajax upload

                # the file is stored raw in the request
                upload = request
                is_raw = True
                # AJAX Upload will pass the filename in the querystring if it
                # is the "advanced" ajax upload
                try:
                    filename = request.GET['qqfile']
                except KeyError:
                    return HttpResponseBadRequest("AJAX request not valid")

            elif 'drpbxURL' in request.GET:
                # This case is for:
                # + dropbox chooser URL submission
                backend = self.get_backend()

                # custom filename handler
                filename = (backend.update_filename(request, filename)
                            or filename)
                # save the file
                backend.setup(filename)

                with open(settings.MEDIA_ROOT + filename, 'wb') as handle:
                    request = requests.get('http://www.example.com/image.jpg', prefetch=False)

                    # In requests 1.0, this would be:
                    # request = requests.get('http://www.example.com/image.jpg', stream=True)

                    for block in request.iter_content(1024):
                        if not block:
                            break

                        handle.write(block)
            else:
                # This is case is for:
                # + fall-back normal file upload
                is_raw = False
                if len(request.FILES) == 1:
                    # FILES is a dictionary in Django but Ajax Upload gives
                    # the uploaded file an ID based on a random number, so it
                    # cannot be guessed here in the code. Rather than editing
                    # Ajax Upload to pass the ID in the querystring, observe
                    # that each upload is a separate request, so FILES should
                    # only have one entry. Thus, we can just grab the first
                    # (and only) value in the dict.
                    upload = request.FILES.values()[0]
                else:
                    raise Http404("Bad Upload")
                filename = upload.name

            if not backend:
                backend = self.get_backend()

                # custom filename handler
                filename = (backend.update_filename(request, filename)
                            or filename)
                # save the file
                backend.setup(filename)

            success = backend.upload(upload, filename, is_raw)
            # callback
            extra_context = backend.upload_complete(request, filename, upload)

            # let Ajax Upload know whether we saved it or not
            ret_json = {'success': success, 'filename': filename}
            if extra_context is not None:
                ret_json.update(extra_context)

            return HttpResponse(json.dumps(ret_json, cls=DjangoJSONEncoder))

ajax_uploader = AjaxFileUploader()
