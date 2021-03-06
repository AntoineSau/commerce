from ast import Try
from nis import cat
from pyexpat import model
from shutil import get_archive_formats
from sre_constants import CATEGORY
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime
from django.db.models import Max
from django.contrib.auth.decorators import login_required

from .models import Bid, User, Auction, Comment, Category, Watchlist


def index(request):

    # Passing in the highest bid for all auctions
    return render(request, "auctions/index.html", {
        # Only taking into account ACTIVE products!
        "auctions": Auction.objects.filter(isactive=True),
        "bids":  Bid.objects.all()
    })

@login_required(login_url='login')
def watchlist(request):
    # Retrieve user's data
    currentuserid = request.user
    currentuserid = currentuserid.id
    return render(request, "auctions/watchlist.html", {
        "auctions": Auction.objects.all(),
        "watchlistsall": Watchlist.objects.all(),
        "userwatcheditems": Watchlist.objects.filter(userwatching=currentuserid),
        "currentuserid": currentuserid
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
@login_required(login_url='login')
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
            "auctions": Auction.objects.filter(isactive=True),
            "bids":  Bid.objects.all()
        })

    else:
        allvalidcategories = Category.objects.exclude(category="Uncategorized")
        return render(request, "auctions/createlisting.html", {
            "categorys": allvalidcategories
        })

def category(request, category):
    category = str(category)
    # Check if the category exists or not
    try:
        categoryid = Category.objects.get(category=category)
        categoryid = categoryid.id
        categoryproducts = Auction.objects.filter(category=categoryid, isactive=True)
        # Making sure we onyl dispaly ACTIVE products of this category

        return render(request, "auctions/category.html", {
            "categoryproducts": categoryproducts,
            "categoryid": categoryid,
            "category": category
            })
    except Category.DoesNotExist:
        
        return render(request, "auctions/categories.html", {
            "categorys": Category.objects.all(),
            "message": "This Category was not found! Please choose from the list below"
        })


def auction(request, auction_id):
    # POST METHOD
    if request.method == "POST":
        
        # We check if there is an Auction with this ID
        try:
            auction = Auction.objects.get(id=auction_id)
            isauctionopen = auction.isactive
            # Retrieving all the comments for this auction
            comments = Comment.objects.filter(auctionid=auction_id)

            # Get user id
            currentuserid = request.user
            currentuserid = currentuserid.id
            currentuserid = User.objects.get(id=currentuserid)

            # Retrieve highest bid:
            highestbid = Bid.objects.filter(auctionid=auction_id)
            # Taking only the highest one
            highestbid = highestbid.order_by('-bid').first

             # Is item in watchlist
            isitemwatched = Watchlist.objects.filter(userwatching=currentuserid, productwatched=auction_id)

            # Check if user wants to delete this item from watchlist / deletefromwatchlist
            if 'deletefromwatchlist' in request.POST:
                
                # Add this itme to this user??s watchlist
                deletefromwatchlist = Watchlist.objects.filter(userwatching=currentuserid, productwatched=auction)
                deletefromwatchlist.delete()


                return render(request, "auctions/auction.html", {
                    "auction": auction,
                    "comments": comments,
                    "auction_id": auction_id,
                    "currentuserid": currentuserid,
                    "isitemwatched": isitemwatched,
                    "message": "Item deleted from watchlist",
                    "isauctionopen": isauctionopen,
                    "highestbid": highestbid
                })


            # Check if user wants to add this item to watchlist / addtowatchlist
            if 'addtowatchlist' in request.POST:
                
                # Add this itme to this user??s watchlist
                addtowatchlist = Watchlist(userwatching=currentuserid, productwatched=auction)
                addtowatchlist.save()


                return render(request, "auctions/auction.html", {
                    "auction": auction,
                    "comments": comments,
                    "auction_id": auction_id,
                    "currentuserid": currentuserid,
                    "isitemwatched": isitemwatched,
                    "isauctionopen": isauctionopen,
                    "message": "Item added to watchlist",
                    "highestbid": highestbid
                })
            
            # Check if user wants to close this auction / closeauction
            if 'closeauction' in request.POST:
                auction = Auction.objects.get(id=auction_id)
                auction.isactive = False
                auction.save()
                return render(request, "auctions/index.html", {
                    "auctions": Auction.objects.filter(isactive=True),
                    "bids":  Bid.objects.all(),
                    "isitemwatched": isitemwatched,
                    "isauctionopen": isauctionopen,
                    "highestbid": highestbid,
                    "messageauctionclosed": "You have closed this auction."
                })
            
            # CHECK IF THERE IS A COMMENT IN POST METHOD FIRST
            if 'comment' in request.POST:

                # Updating comments if there is one:
            
                comment = request.POST["comment"]
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
                    "currentuserid": currentuserid,
                    "isitemwatched": isitemwatched,
                    "commentsubmitted": commentsubmitted,
                    "isauctionopen": isauctionopen,
                })
            
            # IF NO COMMENT, CHECK FOR NEW BID
            elif 'bid' in request.POST:
                
                newbid = request.POST["bid"]
                newbid = float(newbid)

                auction_id = int(auction_id)

                auctiondbid = auction.startingbid
                auctiondbid = float(auctiondbid)

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
                            "currentuserid": currentuserid,
                            "newbid": newbid,
                            "isitemwatched": isitemwatched,
                            "isauctionopen": isauctionopen,
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
                            "currentuserid": currentuserid,
                            "newbid": newbid,
                            "isitemwatched": isitemwatched,
                            "isauctionopen": isauctionopen,
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
                            "currentuserid": currentuserid,
                            "newbid": newbid,
                            "isitemwatched": isitemwatched,
                            "isauctionopen": isauctionopen,
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
                            "currentuserid": currentuserid,
                            "newbid": newbid,
                            "isitemwatched": isitemwatched,
                            "isauctionopen": isauctionopen,
                            "answerno": answerno
                        })
            
            else:
                return render(request, "auctions/index.html", {
                    "auctions": Auction.objects.filter(isactive=True),
                    "bids":  Bid.objects.all(),
                    "isauctionopen": isauctionopen,
                    "message": "Please fill one of the fields and submit it"
                })

        # If the auction doesn't exist, return Index page but with error message
        except Auction.DoesNotExist:
            return render(request, "auctions/index.html", {
                "auctions": Auction.objects.filter(isactive=True),
                "bids":  Bid.objects.all(),
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

            # Retrieving the current highest bid for this item! 

            # Checking if the auction is open!
            isauctionopen = auction.isactive

            # Checking who is the highest bidder

            nobid = None
            auction_id = int(auction_id)
            highestbid = None

            # Retrieving all the watchlist data from the user
            currentuserid = request.user
            currentuserid = currentuserid.id
            isitemwatched = Watchlist.objects.filter(userwatching=currentuserid, productwatched=auction_id)

            try: 
                highestbid = Bid.objects.filter(auctionid=auction_id)
                # Taking only the highest one
                highestbid = highestbid.order_by('-bid')
                highestbid = highestbid.first()
                highestbidder = None
                if highestbid:
                    highestbidder = highestbid.userid

                return render(request, "auctions/auction.html", {
                    "auction": auction,
                    "highestbid": highestbid,
                    "comments": comments,
                    "nobid": nobid,
                    "auction_id": auction_id,
                    "isitemwatched": isitemwatched,
                    "currentuserid": currentuserid,
                    "isauctionopen": isauctionopen,
                    "highestbid": highestbid,
                    "highestbidder": highestbidder
                })

            #except Bid.DoesNotExist:
            except not Bid.objects.filter(auctionid=auction_id):
                nobid = 1

                return render(request, "auctions/auction.html", {
                    "auction": auction,
                    "comments": comments,
                    "nobid": nobid,
                    "auction_id": auction_id,
                    "isitemwatched": isitemwatched,
                    "currentuserid": currentuserid,
                    "isauctionopen": isauctionopen
                })
            

        # If the auction doesn't exist, return Index page but with error message
        except Auction.DoesNotExist:
            return render(request, "auctions/index.html", {
                "auctions": Auction.objects.filter(isactive=True),
                "bids":  Bid.objects.all(),
                "messageok": "This auction was not found! Please check manually below"
            })