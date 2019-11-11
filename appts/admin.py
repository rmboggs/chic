from django.contrib import admin
from .models import Workday, Service, ServiceCategory, Client, Appointment

# Register your models here.
admin.site.register(Workday)
admin.site.register(ServiceCategory)
admin.site.register(Service)
admin.site.register(Client)
