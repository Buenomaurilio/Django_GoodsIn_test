from django.db import models
from warehouses.models import Warehouse

class Checker(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Appointment(models.Model):
    description = models.CharField(max_length=200)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    po = models.CharField(max_length=100)
    qtd_pallet = models.IntegerField()
    hall = models.CharField(max_length=100)
    tipped = models.BooleanField(default=False)
    checked = models.BooleanField(default=False)
    checker = models.ForeignKey(Checker, on_delete=models.SET_NULL, null=True, blank=True)
    arrival_time = models.TimeField(blank=True, null=True)
    check_out_time = models.TimeField(blank=True, null=True)
    bay1 = models.CharField(max_length=100, blank=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, null=True, verbose_name="Observations / Notes")
    # warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)

    STATUS_CHOICES = [
        ('on time', 'On Time'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
        ('no-show', 'No-Show'),
    ]
    status_load = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='on time',
    )

    def __str__(self):
        return f"{self.description} ({self.scheduled_date})"
