from django.urls import path

from . import views

app_name = "Appointments"
urlpatterns = [
    path('', views.index, name='index'),
    path('appointments', views.appointments, name='appointments')
]
