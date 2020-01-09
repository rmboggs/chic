from django.urls import path

from . import views

app_name = "Appointments"
urlpatterns = [
    path('', views.index, name='index'),
    path('appointments', views.appointments, name='appointments'),
    path('appt/<int:app_id>/', views.modify_appointment, name='modify_appointment'),
    path('appt', views.new_appointment, name='new_appointment'),
    path('schedule', views.schedule, name='schedule'),
    path('reports', views.reports, name='reports'),
    path('reports/<str:report_type>', views.reports, name='reports'),
    path('reports/<str:report_type>/<criteria>', views.reports, name='reports'),
]
