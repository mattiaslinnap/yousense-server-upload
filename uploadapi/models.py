from __future__ import absolute_import, division, print_function, unicode_literals
from future_builtins import *  # ascii, filter, hex, map, oct, zip

from django.db import models
from pyshort.djangoshortcuts.fields import ByteaField


class RequestBase(models.Model):
    time_received = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField()
    useragent = models.TextField()

    appid = models.CharField(max_length=100)
    installid = models.CharField(max_length=32)

    class Meta:
        abstract = True

    def __unicode__(self):
        return '{} from {} at {}'.format(self.useragent, self.ip, self.time_received)

def request_base_args(request, appid, installid):
    """Extra keyword arguments for constructing models based on RequestBase.

    time_received is set by the database.
    """
    return {'ip': request.META['REMOTE_ADDR'],
            'useragent': request.META['HTTP_USER_AGENT'],
            'appid': appid,
            'installid': installid}


class BadRequest(RequestBase):
    """File or status upload was rejected for some reason."""
    reason = models.CharField(max_length=250)


class File(RequestBase):
    """Upload of one file."""
    name = models.TextField()
    body = ByteaField()

    def __unicode__(self):
        return self.name

class Status(RequestBase):
    """Upload of current status: files pending upload."""
    pass

    class Meta:
        verbose_name_plural = 'statuses'


class StatusFile(models.Model):
    """A file on the client that may be uploaded later."""
    status = models.ForeignKey(Status)
    directory = models.TextField()
    name = models.TextField()
    size = models.BigIntegerField()

