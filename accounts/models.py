from django.contrib.auth.models import AbstractUser
from django.db import models
from warehouses.models import Warehouse

class CustomUser(AbstractUser):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True)
    is_superadmin = models.BooleanField(default=False)

    def __str__(self):
        return self.username
