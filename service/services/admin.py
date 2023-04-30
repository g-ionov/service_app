from django.contrib import admin
import services.models as models

admin.site.register(models.Service)
admin.site.register(models.Plan)
admin.site.register(models.Subscription)
