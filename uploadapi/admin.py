from django.contrib import admin
from pyshort.djangoshortcuts.admin import readonly_admin

from uploadapi.models import Status, Upload, BadRequest

class RequestAdmin(admin.ModelAdmin):
    list_filter = ('appid', 'installid')

admin.site.register(Status, readonly_admin(Status, RequestAdmin))
admin.site.register(Upload, readonly_admin(Upload, RequestAdmin))
admin.site.register(BadRequest, readonly_admin(BadRequest, RequestAdmin))
