__license__ = "Python"
__copyright__ = "Copyright (C) 2007, Stephen Zabel"
__author__ = "Stephen Zabel - sjzabel@gmail.com"
__contributors__ = "Jay Parlar - parlar@gmail.com"

from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from django.contrib.sites.models import get_current_site

SSL = 'SSL'


class SSLRedirect(object):

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Does connection require security?
        if SSL in view_kwargs:
            secure = view_kwargs[SSL]
            del view_kwargs[SSL]
        else:
            secure = False

        if request.user.is_authenticated():
            secure = True

        # If connection is not secured but requires security, then redirect
        if not self._is_secure(request) and secure:
            return self._redirect(request, secure)

    def _is_secure(self, request):
        if request.is_secure():
            return True

        #Handle the Webfaction case until this gets resolved in the request.is_secure()
        if 'HTTP_X_FORWARDED_SSL' in request.META:
            return request.META['HTTP_X_FORWARDED_SSL'] == 'on'

        return False

    def _redirect(self, request, secure):
        protocol = secure and "https://" or "http://"
        newurl = "%s%s%s" % (protocol, get_current_site(request).domain, request.get_full_path())
        if settings.DEBUG and request.method == 'POST':
            raise RuntimeError, \
        """Django can't perform a SSL redirect while maintaining POST data.
           Please structure your views so that redirects only occur during GETs."""

        return HttpResponsePermanentRedirect(newurl)

