from __future__ import absolute_import, division, print_function, unicode_literals
from future_builtins import *  # ascii, filter, hex, map, oct, zip

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import hashlib
import ujson

from pyshort.strings import printf
from uploadapi.models import File, request_base_args, Status, StatusFile

@csrf_exempt
def file2(request, appid, installid):
    # TODO: Check client version: recent enough, and appid matches User-Agent.

    printf(request.META['HTTP_USER_AGENT'])

    # Validate upload metadata.
    # Filename check
    assert len(request.META['HTTP_NAME']) > 0
    # Length check. Content-Length may be wrong if the body is transparently gzip-encoded.
    assert len(request.body) == int(request.META['HTTP_SIZE'])
    # SHA1 hash check
    expected = request.META['HTTP_SHA1']
    actual = hashlib.sha1(request.body).hexdigest()
    assert expected == actual

    # Save data to DB.
    File.objects.create(name=request.META['HTTP_NAME'],
                        body=request.body,
                        **request_base_args(request, appid, installid))

    # TODO: Start parsing task in background.
    # TODO: log bad requests.
    return HttpResponse('{"success": true}')

@csrf_exempt
def status2(request, appid, installid):
    # TODO: Check client version: recent enough, and appid matches User-Agent.

    assert len(request.body) > 0
    body = ujson.loads(request.body)

    # Validate data
    for dirdata in body['dirs']:
        assert dirdata['name']
        for filedata in dirdata['files']:
            assert filedata['name']
            assert 'size' in filedata

    # Save status.
    # TODO: check transactions.
    status = Status.objects.create(**request_base_args(request, appid, installid))
    for dirdata in body['dirs']:
        dirname = dirdata['name']
        for filedata in dirdata['files']:
            StatusFile.objects.create(status=status,
                                      directory=dirname,
                                      name=filedata['name'],
                                      size=filedata['size'])

    # TODO: log bad requests.
    return HttpResponse('{"success": true}')
