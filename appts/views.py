from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from .models import Appointment, AppointmentForm
import chic.settings

# Create your views here.
def index(request):
    success_message = ""
    context = {}
    form = AppointmentForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            success_message = "Record saved successfully"
            form = AppointmentForm()

    context['message'] = success_message
    context['apptForm'] = form
    #content['debug'] = chic.settings.DEBUG
    return render(request, 'appts/index.html', context)

@login_required(login_url='/login/')
def appointments(request):
    appointment_list = Appointment.objects.all()
    pagi = Paginator(appointment_list, 50)
    page = request.GET.get('page')

    appts = pagi.get_page(page)
    context = {'appointments': appts}
    return render(request, 'appts/appointments.html', context)
