from django.db import models
from django.utils import timezone


class Product(models.Model):
    """"""
    name = models.CharField(max_length=100)
    desciption = models.TextField()
    price = models.DecimalField(max_digits=20, decimal_places=2)
    visible = models.BooleanField(default=False)
    added_on = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
    )

class Category(models.Model):
    category = models.CharField(max_length=100)
