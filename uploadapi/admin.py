from django.contrib import admin
from pyshort.djangoshortcuts.admin import readonly_admin

from uploadapi.models import BadRequest, File, Status

class RequestAdmin(admin.ModelAdmin):
    list_filter = ('appid', 'installid')

admin.site.register(BadRequest, readonly_admin(BadRequest, RequestAdmin))
admin.site.register(File, readonly_admin(File, RequestAdmin))
admin.site.register(Status, readonly_admin(Status, RequestAdmin))