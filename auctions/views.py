from ast import Try
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime
from django.db.models import Max

from .models import Bid, User, Auction, Comment


def index(request):
    return render(request, "auctions/index.html", {
        "auctions": Auction.objects.all(),
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

        # Is there an auction with this ID?
        try:
            auction = Auction.objects.get(id=auction_id)
            
            initialbid = auction.startingbid
            auctionnumber= auction_id
            auction_id = str(auction_id)

            # Retrieve user's bid
            newbid = int(request.POST["bid"])

            # Check current highest bid for this auction
            auction_id = int(auction_id)
            
            # Is there a bid appart form original price
            nobid = None
             
            highestbid = Bid.objects.filter(auctionid=auction_id)
            highestbid = highestbid.order_by('-bid')[0]
            highestbidint = highestbid.bid

            # TESTs comparing new bid, intitial bid and current highest bid:

            # Handle the handle of lack of highest bid
            if newbid > initialbid and highestbidint == None:
                answerok = "Thanks, your had been taken into account!"
                answerno = None
                
                # Check which user is logged in
                currentuserid = request.user
                currentuserid = currentuserid.id
                currentuserid = User.objects.get(id=currentuserid)

                # Register new bid
                newbid = Bid(auctionid=auction, userid=currentuserid, bid=newbid)
                newbid.save()

                # Pull agian the new highest bid to diplay right after saving it
                highestbid = Bid.objects.filter(auctionid=auction_id)
                highestbid = highestbid.order_by('-bid')[0]
                highestbidint = highestbid.bid

            elif newbid < initialbid:
                answerno = "ERROR, please place a bid higher than the original offer"
                answerok = None

            elif newbid > initialbid and newbid > highestbidint:
                answerok = "Thanks, your had been taken into account!"
                answerno = None
                
                # Check which user is logged in
                currentuserid = request.user
                currentuserid = currentuserid.id
                currentuserid = User.objects.get(id=currentuserid)

                # Register new bid
                newbid = Bid(auctionid=auction, userid=currentuserid, bid=newbid)
                newbid.save()

                # Pull agian the new highest bid to diplay right after saving it
                highestbid = Bid.objects.filter(auctionid=auction_id)
                highestbid = highestbid.order_by('-bid')[0]
                highestbidint = highestbid.bid 

            elif newbid < highestbidint:
                answerno = "ERROR, please place a bid higher than the current highest offer"
                answerok = None

            return render(request, "auctions/auction.html", {
                "auction": auction,
                "bid": newbid,
                "answerok": answerok,
                "answerno": answerno,
                "auction_id": auction_id,
                "highestbid": highestbid,
                "nobid": nobid
            })

        except Auction.DoesNotExist:
            return render(request, "auctions/index.html", {
                "auctions": Auction.objects.all(),
                "message": "This auction was not found! Please check manually below"
            })

    # Route if the user just GETs the page
    else:
        # We check if there is an Auction with this ID
        try:
            auction = Auction.objects.get(id=auction_id)
            # Retrieving all the comments for this auction
            auctionnumber = int(auction_id)
            comments = Comment.objects.filter(auctionid=auction_id)

            #Retrieving the current highest bid for this item! ERROR

            nobid = None
            auction_id = int(auction_id)
            highestbid = None

            try: 
                highestbid = Bid.objects.filter(auctionid=auction_id)
                # Taking only the highest one
                highestbid = highestbid.order_by('-bid').first

                return render(request, "auctions/auction.html", {
                    "auction": auction,
                    "highestbid": highestbid,
                    "comments": comments,
                    "nobid": nobid,
                    "auction_id": auction_id
                })

            #except Bid.DoesNotExist:
            except not Bid.objects.filter(auctionid=auction_id):
                nobid = 1

                return render(request, "auctions/auction.html", {
                    "auction": auction,
                    "comments": comments,
                    "nobid": nobid,
                    "auction_id": auction_id
                })
            
            

        # If the auction doesn't exist, return Index page but with error message
        except Auction.DoesNotExist:
            return render(request, "auctions/index.html", {
                "auctions": Auction.objects.all(),
                "message": "This auction was not found! Please check manually below"
            })

    # if auction does not exit, forward to index Django will raise a DoesNotExist exception.!!!!!
    

        
