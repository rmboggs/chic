from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Appointment, AppointmentForm
import chic.settings
from datetime import datetime

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
    post_start_date = request.POST.get('start_date')
    post_end_date = request.POST.get('end_date')

    if post_start_date is not None and post_start_date != '':
        start_date = datetime.strptime(post_start_date, "%Y-%m-%d").date()
    else:
        start_date = None

    if post_end_date is not None and post_end_date != '':
        end_date = datetime.strptime(post_end_date, "%Y-%m-%d").date()
    else:
        end_date = None

    if start_date is not None or end_date is not None:
        if end_date is None:
            appointment_list = Appointment.objects.filter(service_date__gte=start_date)
        elif start_date is None:
            appointment_list = Appointment.objects.filter(service_date__lte=end_date)
        else:
            appointment_list = Appointment.objects.filter(service_date__range=(start_date, end_date))
    else:
        appointment_list = Appointment.objects.all()

    pagi = Paginator(appointment_list, 50)
    page = request.GET.get('page')

    appts = pagi.get_page(page)
    context = {'appointments': appts}

    return render(request, 'appts/appointments.html', context)

@login_required(login_url='/login/')
def new_appointment(request):
    form = AppointmentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            success_message = "Record saved successfully"
            messages.info(request, success_message, extra_tags='alert-success')
            form = AppointmentForm()

    context = {'apptForm': form}
    return render(request, 'appts/appointment.html', context)

@login_required(login_url='/login/')
def modify_appointment(request, app_id):
    appt = get_object_or_404(Appointment, pk=app_id)
    context = { 'appt_id': app_id }

    form = AppointmentForm(request.POST or None, instance=appt)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            success_message = "Record '%i' saved successfully" % (app_id)
            messages.info(request, success_message, extra_tags='success')
            return redirect('/appointments')

    context['apptForm'] = form
    return render(request, 'appts/appointment.html', context)
