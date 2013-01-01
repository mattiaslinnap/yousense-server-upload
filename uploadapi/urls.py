from django.conf.urls import patterns, url

APPID_PATTERN = r'(?P<appid>[0-9a-zA-Z.]{1,100})'
INSTALLID_PATTERN = r'(?P<installid>[0-9a-f]{40})'

urlpatterns = patterns('uploadapi.views',

    # API version 2
    url(r'^2/status/%s/%s/$' % (APPID_PATTERN, INSTALLID_PATTERN), 'status2'),  # Pending upload files.
    url(r'^2/file/%s/%s/$' % (APPID_PATTERN, INSTALLID_PATTERN), 'file2'),  # Log file upload.

)
