from __future__ import absolute_import, division, print_function, unicode_literals
from future_builtins import *  # ascii, filter, hex, map, oct, zip
from collections import defaultdict
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render
import ujson

from uploadapi.models import File, Status
from uploadapi.views import kml
from pyshort.strings import gunzip


def yield_events(ufile):
    for jsontext in gunzip(ufile.body).split('\0'):
        jsontext = jsontext.strip()
        if jsontext:
            yield ujson.loads(jsontext)


@staff_member_required
def index(request):
    installids = list(File.objects.values_list('installid', flat=True).distinct())
    imeimap = defaultdict(list)
    for installid in installids:
        # Search for IMEI in files, stop as soon as found
        found = False
        for ufile in File.objects.filter(installid=installid).order_by('time_received'):
            for event in yield_events(ufile):
                if event['tag'] == 'device.telephony':
                    imei = event['data']['device_id']
                    imeimap[imei].append(installid)
                    found = True
                if found:
                    break
            if found:
                break
    return render(request, 'uploadapi/kmz_index.html', {'imeimap': dict(imeimap), 'installids': installids})


@staff_member_required
def kmz(request, placemark_name):
    try:
        installids = request.GET.getlist('aid')
        assert installids

        fixes = []
        for installid in installids:
            for ufile in File.objects.filter(installid=installid).order_by('time_received'):
                for event in yield_events(ufile):
                    if event['tag'] == 'sensor.gps':
                        fixes.append(event['data'])

        if not fixes:
            return render(request, 'uploadapi/kmz_error.html', {'error': 'No GPS data.'}, status=404)

        fixes.sort(key=lambda fix: fix['time'])
        response = HttpResponse(kml.kmz({placemark_name: fixes}), content_type='application/vnd.google-earth.kmz')
        response['Content-Disposition'] = 'attachment; filename="yousense.kmz"'
        return response

    except (AssertionError, KeyError):
        raise
        return render(request, 'uploadapi/kmz_error.html', status=404)
