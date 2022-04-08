from unicodedata import category
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import BooleanField
from django.forms import DateTimeField

class User(AbstractUser):
    pass

class Auction(models.Model):
	title = models.CharField(max_length=50)
	description = models.TextField(max_length=500)
	startingbid = models.FloatField()
	image = models.URLField()
	category = models.CharField(max_length=15)
	dateuploaded = models.DateTimeField()
	isactive = models.BooleanField(default=True)



# TO DO: 3 MODELS :
# auction listing ALL NEEDED
# bids
# comments made on auction listings.