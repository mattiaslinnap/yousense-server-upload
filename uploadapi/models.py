from django.db import models
from pyshort.djangoshortcuts.fields import ByteaField


class RequestFields(models.Model):
    time_received = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField()
    useragent = models.TextField(blank=True)

    appid = models.CharField(max_length=40)
    installid = models.CharField(max_length=40)

    class Meta:
        abstract = True


class BlockFields(models.Model):
    # Block identifiers: first object counters
    counter_restart = models.BigIntegerField()  # App restart counter
    counter_block = models.BigIntegerField()  # Block counter
    counter_obj = models.BigIntegerField()  # First object counter
    time_system = models.BigIntegerField()
    time_realtime = models.BigIntegerField()
    time_uptime = models.BigIntegerField()

    class Meta:
        abstract = True


class BadRequest(RequestFields):
    """Block or status upload was rejected for some reason."""
    reason = models.CharField(max_length=250)


class Block(RequestFields, BlockFields):
    """Upload of one block of data."""

    gzipped_data = ByteaField()
    sha1 = models.CharField(max_length=40)


class Status(RequestFields):
    """Upload of current status: blocks pending update."""
    pass


class PendingBlock(BlockFields):
    """A single block without data, part of a status."""
    status = models.ForeignKey(Status)


