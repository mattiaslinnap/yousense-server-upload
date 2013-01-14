from django.db import models
from pyshort.djangoshortcuts.fields import ByteaField


class RequestBase(models.Model):
    time_received = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField()
    useragent = models.TextField(blank=True)

    appid = models.CharField(max_length=40)
    installid = models.CharField(max_length=40)

    class Meta:
        abstract = True


class BadRequest(RequestBase):
    """File or status upload was rejected for some reason."""
    reason = models.CharField(max_length=250)


class File(RequestBase):
    """Upload of one file."""

    name = models.TextField(blank=False, null=False)
    body = ByteaField()


class Status(RequestBase):
    """Upload of current status: files pending upload."""
    pass


class PendingFile(models.Model):
    """A pending file without data, part of a status."""
    status = models.ForeignKey(Status)
    name = models.TextField(blank=False, null=False)
    size = models.BigIntegerField()

