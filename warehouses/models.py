from django.db import models

class Warehouse(models.Model):
    name = models.CharField(max_length=100, unique=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
