from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def file2(appid, installid):
    # Check client version.
    # Validate upload metadata: SHA1, client path.
    # Save data to DB.
    pass

@csrf_exempt
def status2(appid, installid):
    # Check client version.
    # Parse data, validate
    # Save status.
    pass
