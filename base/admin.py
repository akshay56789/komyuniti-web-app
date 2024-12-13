from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.User)
admin.site.register(models.Groups)
admin.site.register(models.Club)
admin.site.register(models.Post)
admin.site.register(models.User_Request)
admin.site.register(models.Comments)
admin.site.register(models.Events)
admin.site.register(models.Tags)
admin.site.register(models.Club_post)
admin.site.register(models.Club_Comment)