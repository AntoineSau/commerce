from ast import Try
from pyexpat import model
from shutil import get_archive_formats
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

        return render(request, "auctions/index.html", {
            "auctions": Auction.objects.all()
        })

    else:
        return render(request, "auctions/createlisting.html")

def auction(request, auction_id):
    # POST METHOD
    if request.method == "POST":
        
        # We check if there is an Auction with this ID
        try:
            auction = Auction.objects.get(id=auction_id)
            # Retrieving all the comments for this auction
            auctionnumber = int(auction_id)
            comments = Comment.objects.filter(auctionid=auction_id)

            # Updating new comment is there is one in post method:

            if 'comment' in request.POST:

                # Updating comments if there is one:
            
                comment = request.POST["comment"]
                currentuserid = request.user
                currentuserid = currentuserid.id
                currentuserid = User.objects.get(id=currentuserid)
                newcommenttosave = Comment(auctionid=auction, userid=currentuserid, comment=comment)
                newcommenttosave.save()

                # Save cofnriamtion message if comment has been uploaded
                commentsubmitted = "Your comment has been submitted, thank you!"

                # Pulling once again all comment inclduign the new one:
                comments = Comment.objects.filter(auctionid=auction_id)

                highestbid = Bid.objects.filter(auctionid=auction_id)
                # Taking only the highest one
                highestbid = highestbid.order_by('-bid').first

                return render(request, "auctions/auction.html", {
                    "auction": auction,
                    "highestbid": highestbid,
                    "comments": comments,
                    "auction_id": auction_id,
                    "commentsubmitted": commentsubmitted
                })
                
            else:
                newbid = request.POST["bid"]
                currentuserid = request.user
                currentuserid = currentuserid.id
                currentuserid = User.objects.get(id=currentuserid)
                newbidtosave = Bid(auctionid=auction, userid=currentuserid, bid=newbid)
                newbidtosave.save()
            
            

                #Retrieving the current highest bid for this item! 

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
                        "auction_id": auction_id,
                        "newbid": newbid
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



    # GET METHOD
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