from django.shortcuts import render
from .models import Appointment

# Create your views here.
def index(request):
    return render(request, 'appts/index.html')
