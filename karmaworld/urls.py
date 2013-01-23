from django.contrib import admin
from django.conf.urls.defaults import patterns, include, url
from django.views.generic import ListView, DetailView
from django.views.generic.simple import direct_to_template

from karmaworld.apps.ajaxuploader.views import ajax_uploader
from karmaworld.apps.courses.models import Course
from karmaworld.apps.courses.views import CourseDetailView
from karmaworld.apps.notes.views import NoteDetailView, RawNoteDetailView, raw_file

# See: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#hooking-adminsite-instances-into-your-urlconf
admin.autodiscover()

# See: https://docs.djangoproject.com/en/dev/topics/http/urls/
urlpatterns = patterns('',
    # Admin panel and documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^about/$', direct_to_template, { 'template': 'about.html' }, name='about'),

    # the raw route must come before routes with a capture group after the
    # first / of the url
    url(r'^raw/(?P<pk>\d+)$', raw_file, name='note_raw'),
    url(r'^(?P<school_slug>[^/]+)/(?P<slug>[^/]+)$', \
        CourseDetailView.as_view(), name='course_detail'),
    # note file as id
    url(r'^(?P<school_slug>[^/]+)/(?P<course_slug>[^/]+)/(?P<pk>[\d^/]+)$', \
        NoteDetailView.as_view(), name='note_detail'),
    # note file by note.slug
    url(r'^(?P<school_slug>[^/]+)/(?P<course_slug>[^/]+)/(?P<slug>[^/]+)$', \
        NoteDetailView.as_view(), name='note_detail'),

    # uploading
    url(r'ajax-upload$', ajax_uploader, name='ajax_upload'),

    url(r'^$', ListView.as_view(model=Course), name='home'),
)
