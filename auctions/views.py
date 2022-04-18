from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime

from .models import Bid, User, Auction


def index(request):
    return render(request, "auctions/index.html", {
        "auctions": Auction.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

# Adding a nre view for user to create a new listing

def createlisting(request):
    if request.method == "POST":
        # Retrieving data from the user / user passed in automatically as {{ user }} / {{ user.id }}
        currentuserid = request.user
        currentuserid = currentuserid.id
        currentuserid = User.objects.get(id=currentuserid)
        newtitle = request.POST["title"]
        newdescription = request.POST["description"]
        newstartingbid = request.POST["startingbid"]
        newimageurl = request.POST["imageurl"]
        newcategory = request.POST["category"]

        # Save user listing in database, @ Auction Model, only with mandatory fields
        newauction = Auction(userid=currentuserid, title=newtitle, description=newdescription, startingbid=newstartingbid, image=newimageurl, category=newcategory)
        newauction.save()

        #Test prnt only
        #return render(request, "auctions/createlisting.html", {
        #   "title": newtitle,
        #    "description": newdescription,
        #    "startingbid": newstartingbid,
        #    "imageurl": newimageurl,
        #    "category": newcategory
        # })

        return render(request, "auctions/index.html", {
            "auctions": Auction.objects.all()
        })

    else:
        return render(request, "auctions/createlisting.html")

def auction(request, auction_id):
    if request.method == "POST":

        try:
            auction = Auction.objects.get(id=auction_id)
            initialbid = auction.startingbid
            
            auction_id = str(auction_id)

            newbid = int(request.POST["bid"])
            
            # TEST comparing bid and intitial bid:
            if newbid > initialbid:
                answerok = "Thanks, your had been taken into account!"
                answerno = None
                
                # Check which user is logged in
                currentuserid = request.user
                currentuserid = currentuserid.id
                currentuserid = User.objects.get(id=currentuserid)

                # Register new bid
                newbid = Bid(auctionid=auction, userid=currentuserid, bid=newbid)
                newbid.save()

            elif newbid < initialbid:
                answerno = "ERROR, please place higher bid!"
                answerok = None
            return render(request, "auctions/auction.html", {
                "auction": auction,
                "bid": newbid,
                "answerok": answerok,
                "answerno": answerno,
                "auction_id": auction_id
            })

        except Auction.DoesNotExist:
            return render(request, "auctions/index.html", {
                "auctions": Auction.objects.all(),
                "message": "This auction was not found! Please check manually below"
            })

    else:
        try:
            auction = Auction.objects.get(id=auction_id)

            #TO DO!!! Retrieve current highest bid fot this item!
            auction_id = int(auction_id)
            otherbid = "TODO"

            return render(request, "auctions/auction.html", {
                "auction": auction,
                "otherbid": otherbid
            })

        except Auction.DoesNotExist:
            return render(request, "auctions/index.html", {
                "auctions": Auction.objects.all(),
                "message": "This auction was not found! Please check manually below"
            })

    # if auction does not exit, forward to index Django will raise a DoesNotExist exception.!!!!!
    

        
