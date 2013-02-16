from __future__ import absolute_import, division, print_function, unicode_literals
from future_builtins import *  # ascii, filter, hex, map, oct, zip

from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection
from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from pyshort.strings import printf, gunzip

from uploadapi.models import File, Status

@staff_member_required
def index(request):
    # Assuming no file uploads happen before a status report.
    apps = []
    for appid in Status.objects.values_list('appid', flat=True).order_by('appid').distinct():
        app = {}
        app['name'] = appid
        app['total_installs'] = Status.objects.filter(appid=appid).values_list('installid', flat=True).distinct().count()
        app['total_files'] = File.objects.filter(appid=appid).count()
        app['total_bytes'] = File.objects.filter(appid=appid).aggregate(Sum('size'))['size__sum']
        if not app['total_bytes']:
            app['total_bytes'] = 0
        app['total_statuses'] = Status.objects.filter(appid=appid).count()
        app['installs'] = []
        for installid in Status.objects.filter(appid=appid).values_list('installid', flat=True).order_by('installid').distinct():
            inst = {}
            inst['installid'] = installid
            latest_status = Status.objects.filter(appid=appid, installid=installid).latest()
            # TODO: Consider File and BadRequest in latest request time.
            inst['latest_request'] = latest_status.time_received
            inst['files'] = File.objects.filter(appid=appid, installid=installid).count()
            inst['bytes'] = File.objects.filter(appid=appid, installid=installid).aggregate(Sum('size'))['size__sum']
            if not inst['bytes']:
                inst['bytes'] = 0
            inst['pending_files'] = latest_status.statusfile_set.filter(directory='yousense-upload').count()
            inst['pending_bytes'] = latest_status.statusfile_set.filter(directory='yousense-upload').aggregate(Sum('size'))['size__sum']
            if not inst['pending_bytes']:
                inst['pending_bytes'] = 0
            app['installs'].append(inst)
        apps.append(app)

    for q in connection.queries:
        printf('{time}sec: {sql}', **q)
    return render(request, 'uploadapi/dashboard.html', {'apps': apps})


@staff_member_required
def install_files(request, appid, installid):
    try:
        status = Status.objects.filter(appid=appid, installid=installid).latest()
    except Status.DoesNotExist:
        raise Http404('User %s on %s has uploaded no status reports.' % (installid, appid))
    files = list(File.objects.filter(appid=appid, installid=installid).order_by('-time_received'))
    return render(request, 'uploadapi/install_files.html', {'status': status, 'files': files})


@staff_member_required
def install_file_data(request, appid, installid, fileid):
    ufile = get_object_or_404(File, appid=appid, installid=installid, pk=fileid)
    events = gunzip(ufile.body).split('\0')
    return render(request, 'uploadapi/install_file_data.html', {'file': ufile, 'events': events})