from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator 
from datetime import timedelta

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
    service_time = models.DurationField(default=timedelta(hours=1))
    default_price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.service_name

class Client(models.Model):
    phone = models.BigIntegerField(primary_key=True, validators=[MinValueValidator(1000000000), MaxValueValidator(9999999999)])
    name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return "%s - %s" % (self.phone, self.name)

class Appointment(models.Model):
    client = models.ForeignKey(Client, on_delete = models.PROTECT)
    service = models.ForeignKey(Service, on_delete = models.PROTECT)
    appointment_time = models.DateTimeField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    completed = models.BooleanField(null=True, default=None)
    
    def __str__(self):
        return "%s > %s" % (self.appointment_time.strftime("%Y %B %d - %-I:%M %p"),
                            str(self.client))
