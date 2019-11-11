from django.contrib import admin
from .models import Workday, Service, ServiceCategory, Client, Appointment

admin.site.site_header = "Chic Appointments Admin"
admin.site.site_title = "Chic Appointments Admin Area"
admin.site.index_title = "Welcome to the appointment admin area"

# Register your models here.
admin.site.register(Workday)
admin.site.register(ServiceCategory)
admin.site.register(Service)
admin.site.register(Client)
