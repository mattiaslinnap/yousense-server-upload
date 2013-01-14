from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import hashlib

from uploadapi.models import File

@csrf_exempt
def file2(request, appid, installid):
    # Check client version: recent enough, and appid matches User-Agent.

    # Validate upload metadata.
    # Filename check
    assert len(request.META['HTTP_NAME']) > 0
    # Length check. Content-Length may be wrong if the body is transparently gzip-encoded.
    assert len(request.body) == len(request.META['HTTP_SIZE'])
    # SHA1 hash check
    expected = request.META['HTTP_SHA1']
    actual = hashlib.sha1(request.body).hexdigest()
    assert expected == actual

    # Save data to DB.
    File.objects.create(ip=request.META['REMOTE_ADDR'],
                        useragent=request.META['HTTP_USER_AGENT'],
                        appid=appid,
                        installid=installid,
                        name=request.META['HTTP_NAME'],
                        body=request.body)

    # Start parsing task in background.

    return HttpResponse('{"success": true}')

@csrf_exempt
def status2(request, appid, installid):
    # Check client version: recent enough, and appid matches User-Agent.

    # Parse data, validate
    # Save status.
    print request.body
    return HttpResponse('{"success": true}')
