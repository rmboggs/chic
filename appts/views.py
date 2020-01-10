from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncYear, TruncMonth, TruncQuarter, TruncDate, ExtractYear, ExtractQuarter
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from .models import Appointment, AppointmentForm
import chic.settings
from datetime import datetime, time, date
import csv

# Create your views here.
def index(request):
    return render(request, 'appts/index.html')

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
    msgs = messages.get_messages(request)

    if msgs is not None and msgs:
        appt = Appointment()
        appt_date = None
        for m in msgs:
            if m.extra_tags == 'default-service-date':
                appt_date = m.message
                break

        if appt_date is not None:
            schedule_date = datetime.strptime(appt_date, "%Y-%m-%d")
            new_hour = datetime.now().time().hour + 1
            new_time = time(new_hour, 0, 0)
            appt.service_date = datetime.combine(schedule_date.date(), new_time)

        form = AppointmentForm(instance=appt)
    else:
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
            messages.info(request, success_message, extra_tags='alert-success')
            return redirect('/appointments')

    context['apptForm'] = form
    return render(request, 'appts/appointment.html', context)

@login_required(login_url='/login/')
def schedule(request):
    context = {}

    if request.method == 'POST':
        appt_date = request.POST.get('appt_date')
        is_new = request.POST.get('new')
        get_appts = request.POST.get('get')

        if appt_date is None:
            msg = "Please provide a date of the schedule to retrieve"
            messages.info(request, msg, extra_tags='alert-danger')
            return render(request, 'appts/schedule.html')

        if is_new is not None:
            messages.info(request, appt_date, extra_tags='default-service-date')
            return redirect('/appt')

        if get_appts is not None:
            schedule_date = datetime.strptime(appt_date, "%Y-%m-%d")
            items = Appointment.objects.filter(service_date__date=schedule_date)
            context['appts'] = items

    return render(request, 'appts/schedule.html', context)

@login_required(login_url='/login/')
def reports(request, report_type=None):
    report_template = 'appts/reports.html'

    if report_type is None:
        return render(request, report_template)

    if request.method == 'POST':
        criteria = request.POST.get('criteria')
    else:
        criteria = None

    # get the initial list of Appointments
    appt_list = Appointment.objects.filter(Q(cash_sales__gt=0) | Q(credit_sales__gt=0)).annotate(year=ExtractYear('service_date'), month=TruncMonth('service_date'), quarter=ExtractQuarter('service_date'), service_day=TruncDate('service_date')).values('year', 'month', 'quarter', 'service_day', 'service_date', 'cash_sales', 'credit_sales')
    report_type_l = report_type.lower()
    context = {'report_type': report_type_l}
    default_date = datetime.now()

    if report_type_l == "day":

        if criteria is not None and len(criteria) > 0:
            filter_date = datetime.strptime(criteria, "%Y-%m-%d")
        else:
            filter_date = default_date.date()

        filtered_items = appt_list.filter(service_date__year=filter_date.year).filter(service_date__month=filter_date.month)
        group_items = filtered_items.values('service_day').order_by('service_day')

        context['search_value'] = filter_date.strftime("%Y-%m-%d")
        context['report_name'] = "Appointments by Date"
    elif report_type_l == "month":
        if criteria is not None and len(criteria) > 0:
            try:
                filter_year = int(criteria)
            except:
                raise Http404("criteria is not numeric")
        else:
            filter_year = default_date.year

        filtered_items = appt_list.filter(year=filter_year)
        group_items = filtered_items.values('month').order_by('month')

        context['search_value'] = str(filter_year)
        context['report_name'] = "Appointments by month"
    elif report_type_l == 'quarter':
        if criteria is not None and len(criteria) > 0:
            try:
                filter_year = int(criteria)
            except:
                raise Http404("criteria is not numeric")
        else:
            filter_year = default_date.year

        filtered_items = appt_list.filter(year=filter_year)
        group_items = filtered_items.values('year', 'quarter').order_by('year', 'quarter')

        context['search_value'] = str(filter_year)
        context['report_name'] = "Appointments by quarter"
    elif report_type_l == "year":
        filtered_items = appt_list
        group_items = filtered_items.values('year').order_by('year')

        context['report_name'] = "Appointments by year"
    else:
        raise Http404("Unrecognized report type: %s" % (report_type,))

    items = group_items.annotate(appt_count=Count('id'), cash=Sum('cash_sales'), credit=Sum('credit_sales'), total=Sum('cash_sales')+Sum('credit_sales'))
    totals = filtered_items.aggregate(appt_count=Count('id'), cash=Sum('cash_sales'), credit=Sum('credit_sales'), total=Sum('cash_sales')+Sum('credit_sales'))

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == "Export":
            # Create the HttpResponse object with the appropriate CSV header.
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="%s_%s.csv"' % (report_type_l, context['search_value'])

            writer = csv.writer(response)
            header = [report_type_l, "Count", "Cash Sales", "Credit Sales", "Total Sales"]

            writer.writerow(header)

            for item in items:
                writer.writerow(list(item.values()))

            tmp_list = ["Grand total"]
            tmp_list.append(totals["appt_count"])
            tmp_list.append(totals["cash"])
            tmp_list.append(totals["credit"])
            tmp_list.append(totals["total"])
            writer.writerow(tmp_list)

            return response

    context['totals'] = totals
    context['items'] = items

    return render(request, report_template, context)
