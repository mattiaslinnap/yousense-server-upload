from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def file2(request, appid, installid):
    # Check client version.
    # Validate upload metadata: SHA1, client path.
    # Save data to DB.
    print request.body
    return HttpResponse('{"success": true}')

@csrf_exempt
def status2(request, appid, installid):
    # Check client version.
    # Parse data, validate
    # Save status.
    print request.body
    return HttpResponse('{"success": true}')
