from django.shortcuts import render
from .models import Appointment, AppointmentForm

# Create your views here.
def index(request):
    success_message = ""
    form = AppointmentForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            success_message = "Record saved successfully"
            form = AppointmentForm()

    return render(request, 'appts/index.html', {'message':success_message, 'apptForm': form})
