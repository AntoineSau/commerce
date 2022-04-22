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

from .models import Bid, User, Auction, Comment, Category


def index(request):

    # TO DO Need to pass in the highest bid for all auctions
    bids = Bid.objects.all()

    
    
    return render(request, "auctions/index.html", {
        "auctions": Auction.objects.all(),
        "bids": bids
    })

def categories(request):

    return render(request, "auctions/categories.html", {
        "categorys": Category.objects.all()
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
        categoryid = request.POST["category"]

        newcategory = Category.objects.get(id=categoryid)

        # Save user listing in database, @ Auction Model, only with mandatory fields
        newauction = Auction(userid=currentuserid, title=newtitle, description=newdescription, startingbid=newstartingbid, highestbid=newstartingbid, image=newimageurl, category=newcategory)
        newauction.save()

        return render(request, "auctions/index.html", {
            "auctions": Auction.objects.all()
        })

    else:
        allvalidcategories = Category.objects.exclude(category="Uncategorized")
        return render(request, "auctions/createlisting.html", {
            "categorys": allvalidcategories
        })

def auction(request, auction_id):
    # POST METHOD
    if request.method == "POST":
        
        # We check if there is an Auction with this ID
        try:
            auction = Auction.objects.get(id=auction_id)
            # Retrieving all the comments for this auction
            auctionnumber = int(auction_id)
            comments = Comment.objects.filter(auctionid=auction_id)

            # CHECK IF THERE IS A COMMENT IN POST METHOD FIRST
            if 'comment' in request.POST:

                # Updating comments if there is one:
            
                comment = request.POST["comment"]
                currentuserid = request.user
                currentuserid = currentuserid.id
                currentuserid = User.objects.get(id=currentuserid)
                newcommenttosave = Comment(auctionid=auction, userid=currentuserid, comment=comment)
                newcommenttosave.save()

                # Save confirmation message if comment has been uploaded
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
            
            # IF NO COMMENT, CHECK FOR NEW BID
            elif 'bid' in request.POST:
                
                newbid = request.POST["bid"]
                newbid = int(newbid)

                currentuserid = request.user
                currentuserid = currentuserid.id
                currentuserid = User.objects.get(id=currentuserid)
                auction_id = int(auction_id)

                auctiondbid = auction.startingbid
                auctiondbid = int(auctiondbid)

                nobid = None
                auction_id = int(auction_id)
                highestbid = Bid.objects.filter(auctionid=auction_id)
                # Taking only the highest one
                highestbid = highestbid.order_by('-bid')
                highestbid = highestbid.first()
                
                
                if highestbid is not None:
                    highestbid = highestbid.bid
                    if newbid > highestbid:

                        newbidtosave = Bid(auctionid=auction, userid=currentuserid, bid=newbid)
                        newbidtosave.save()

                        # Udpate only highestbid field @ Auctions
                        auction = Auction.objects.get(id=auction_id)
                        auction.highestbid = newbid
                        auction.save()

                        # Update the highest bid for this auction @ Auciton Model!! auction.highestbid 

                        answerok = "Your bid has been registered, thank you!"
                        # Query agian the highest bid to show it again
                        highestbid = newbidtosave
                        return render(request, "auctions/auction.html", {
                            "auction": auction,
                            "highestbid": highestbid,
                            "comments": comments,
                            "nobid": nobid,
                            "auction_id": auction_id,
                            "newbid": newbid,
                            "answerok": answerok
                    })

                    else:
                        answerno = "Please place a higher bid. It must be higher than the initial bid and any other additional bid!"
                        highestbid = Bid.objects.filter(auctionid=auction_id)
                        # Query agian the highest bid to show it again
                        highestbid = highestbid.order_by('-bid').first
                        return render(request, "auctions/auction.html", {
                            "auction": auction,
                            "highestbid": highestbid,
                            "comments": comments,
                            "nobid": nobid,
                            "auction_id": auction_id,
                            "newbid": newbid,
                            "answerno": answerno
                        })

                else:    

                    if newbid > auctiondbid:

                        newbidtosave = Bid(auctionid=auction, userid=currentuserid, bid=newbid)
                        newbidtosave.save()
                        
                        # Udpate only highestbid field @ Auctions
                        auction = Auction.objects.get(id=auction_id)
                        auction.highestbid = newbid
                        auction.save()

                        answerok = "Your bid has been registered, thank you!"
                        highestbid = newbidtosave
                        return render(request, "auctions/auction.html", {
                            "auction": auction,
                            "highestbid": highestbid,
                            "comments": comments,
                            "nobid": nobid,
                            "auction_id": auction_id,
                            "newbid": newbid,
                            "answerok": answerok
                    })

                    else:
                        answerno = "Please place a higher bid"
                        return render(request, "auctions/auction.html", {
                            "auction": auction,
                            "highestbid": highestbid,
                            "comments": comments,
                            "nobid": nobid,
                            "auction_id": auction_id,
                            "newbid": newbid,
                            "answerno": answerno
                        })
            
            else:
                return render(request, "auctions/index.html", {
                    "auctions": Auction.objects.all(),
                    "message": "Please fill one of the fields and submit it"
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