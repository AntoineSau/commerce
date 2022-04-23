import imghdr
from tkinter import CASCADE
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

class Category(models.Model):
    category = models.CharField(max_length=20)

    def __str__(self):
        return f"Category number {self.id}: {self.category}"

class Auction(models.Model):
    userid = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    startingbid = models.FloatField(default=1)
    highestbid = models.FloatField(default=1)
    image = models.URLField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="cat")
    dateuploaded = models.DateTimeField(default=datetime.now,)
    isactive = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}. Category: {self.category}. Starting bid: {self.startingbid} Euros"

class Bid(models.Model):
    auctionid = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bidauction")
    userid = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userid")
    bid = models.FloatField()
    dateofbid = models.DateTimeField(default=datetime.now,)

    def __str__(self):
        return f"Bid number {self.id}. Made by {self.userid} on {self.auctionid} for {self.bid} Euros on {self.dateofbid}"

class Comment(models.Model):
    auctionid = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="commentauction")
    userid = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usercomment")
    comment = models.TextField(max_length=500)
    dateofbid = models.DateTimeField(default=datetime.now,)

    def __str__(self):
        return f"Comment number {self.id}. Made by {self.userid} on {self.auctionid}: '{self.comment}', commented on {self.dateofbid}"




# TO DO
# add "Categories" models
# add category watchlist
# Link models manay ot many
