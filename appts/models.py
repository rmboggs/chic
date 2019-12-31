from datetime import timedelta
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.forms import ModelForm
from django.utils import timezone


# Create your models here.
class Workday(models.Model):
    days_of_the_week = {
        0: 'Sunday',
        1: 'Monday',
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday'
    }
    WEEKDAY_IDS = [(k, v) for k,v in days_of_the_week.items()]
    day_of_week = models.SmallIntegerField(primary_key=True, choices=WEEKDAY_IDS)
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)

    def __str__(self):
        return self.days_of_the_week[self.day_of_week]

class ServiceCategory(models.Model):
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name = "Service Category"
        verbose_name_plural = "Service Categories"

class Service(models.Model):
    service_name = models.CharField(max_length=100)
    category = models.ForeignKey(ServiceCategory, on_delete = models.PROTECT)
    service_time = models.DurationField(default=timedelta(hours=1), help_text="The expected amount of time")
    default_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.service_name

class Client(models.Model):
    phone = models.BigIntegerField(primary_key=True, validators=[MinValueValidator(1000000000), MaxValueValidator(9999999999)], help_text="Phone number of the client")
    name = models.CharField(max_length=100, help_text="Name of the client")
    email = models.EmailField(null=True, blank=True, help_text="Email address of the client [optional]")

    def __str__(self):
        return "%s - %s" % (self.phone, self.name)

class Appointment(models.Model):
    client = models.ForeignKey(Client, blank=True, null=True, on_delete = models.PROTECT, help_text="Contact information of an existing client")
    client_name = models.CharField(max_length=100, blank=True, help_text="Name of the client [optional]", verbose_name="Client Name")
    service = models.ForeignKey(Service, on_delete = models.PROTECT, help_text="The type of service the appointment is for")
    stylist = models.ForeignKey(User, on_delete = models.PROTECT, help_text="The stylist that the appointment is assigned to")
    service_date = models.DateTimeField(default=timezone.now, blank=False, null=False, verbose_name="Date of service", help_text="Date and/or time that service was completed")
    cash_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=False, null=False, help_text="Total amount paid by customer", validators=[MinValueValidator(0)])
    credit_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=False, null=False, help_text="Total amount paid by customer", validators=[MinValueValidator(0)])

    @property
    def total_sales(self):
        return self.cash_sales + self.credit_sales

    User.__str__ = lambda user: user.get_full_name() or user.get_username()

    class Meta:
        ordering = ['service_date',]

class AppointmentForm(ModelForm):
    class Meta:
      model = Appointment
      fields = ['client_name', 'service', 'stylist', 'service_date', 'cash_sales', 'credit_sales']
