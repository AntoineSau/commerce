from unicodedata import category
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import BooleanField
from django.forms import DateTimeField
from datetime import datetime

class User(AbstractUser):
    pass

    def __str__(self):
        return f"User Name: {self.username}. User ID number: {self.id}."

class Auction(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    startingbid = models.FloatField()
    image = models.URLField()
    category = models.CharField(max_length=15)
    dateuploaded = models.DateTimeField(default=datetime.now,)
    isactive = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} / Category: {self.category} / Starting bid: {self.startingbid} Euros"

# TO DO: 3 MODELS :
# auction listing ALL NEEDED
# bids
# comments made on auction listings.