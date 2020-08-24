from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms

from .models import User, AuctionListing, Bid, Comment, WatchList


class NewListing(forms.Form):
    
    title = forms.CharField(label="NewListing Title", max_length=64)
    description = forms.CharField(label="About the NewListing", widget=forms.Textarea)
    startbid = forms.IntegerField(label="Start Bid for NewListing")
    picurl = forms.CharField(label="URL for the related photo")
    category = forms.CharField(label="Category")


def index(request):
    
    ac_listings = AuctionListing.objects.filter(active=True)
    message = 0
    bought = 0
    
    user = request.user
    listings = AuctionListing.objects.all()
    for listing in listings:
        if listing.buyer == user:
            bought = listing
            message = f"Congratulations!! You won the auction of {bought}"

    return render(request, "auctions/index.html", {
        "message": message,
        "bought": bought,
        "listings": ac_listings
        })


def listing(request, listing_id):
    
    prod = AuctionListing.objects.get(id=listing_id)
    close = 0

    if not request.user.is_authenticated:
        message = "Please login to bid/comment."
        watching = 0


    else:
        user = request.user
        if prod.seller == user:
            close = "Close Auction on this Product"

        watches = WatchList.objects.all()
        ctr = 0
        for watch in watches:
            if watch.watcher == user:
                ctr += 1

        if ctr == 0:
            watching="Add to my WatchList"
        elif ctr == 1:
            newwatch = WatchList.objects.get(watcher=user)
            if prod in newwatch.product.all():
                watching = "Remove from my WatchList"
            else:
                watching = "Add to my WatchList"

        message = 0
        user = request.user
        if request.method == "POST":
            
            if 'comments' in request.POST:
                newcomment = request.POST["newcomment"]
                ncomment = Comment(commenter=user, product=prod, comment=newcomment)
                ncomment.save()

            elif 'addbid' in request.POST :
                newbid = request.POST["bid"]
                nbid = Bid(bidder=user, product=prod, latest_bid=int(newbid))
                nbid.save()
                """return render(request, "auctions/listing.html", {
                        "item": prod,
                        "comments": prod.comment.all(),
                        "message": message,
                        "watching": watching,
                        "close": close,
                        "bidform": NewBid()
                        })"""


    return render(request, "auctions/listing.html", {
        "item": prod,
        "comments": prod.comment.all(),
        "logged_out": message,
        "close": close,
        "logged_in": watching
        })


def createnew(request):
    
    if request.method=="POST":
        form = NewListing(request.POST)
        if form.is_valid():
            newtitle=form.cleaned_data["title"]
            description=form.cleaned_data["description"]
            startbid=form.cleaned_data["startbid"]
            picurl=form.cleaned_data["picurl"]
            category=form.cleaned_data["category"]
            newlisting = AuctionListing(title=newtitle, description=description, start_bid=startbid, pic_url=picurl, category=category, seller=request.user)
            newlisting.save()

            return HttpResponseRedirect(reverse("index"))

        else:
            return render(request, "auctions/newprod.html", {
                "form": form
                })

    return render(request, "auctions/newprod.html", {
        "form": NewListing()
        })


def closeauction(request, listing_id):
    
    prod = AuctionListing.objects.get(id=listing_id)
    biddings = Bid.objects.filter(product=prod)
    winning_bidding = 0
    
    final_price = prod.start_bid
    for bidding in biddings:
        if final_price <= bidding.latest_bid:
            final_price = bidding.latest_bid
            winning_bidding = bidding

    prod.active = False
    
    if not winning_bidding:
        prod.buyer = prod.seller
    else:
        prod.buyer = winning_bidding.bidder
    
    prod.save()
    message = "Your Product has been taken off the e-auctions"

    return render(request, "auctions/closed.html", {
        "message": message,
        "listing": prod,
        "winner": winning_bidding
        })


def watchlist(request):
    
    user = request.user
    ctr = WatchList.objects.get(watcher=user)
    items = ctr.product.all()
    return render(request, "auctions/watchlist.html", {
        "listings": items
        })


def addedwatchlist(request, listing_id):
    
    user = request.user
    prod = AuctionListing.objects.get(id=listing_id)
    
    watches = WatchList.objects.all()
    ctr = 0
    for watch in watches:
        if watch.watcher == user:
            ctr += 1

    if ctr == 0:
        newwatch = WatchList(watcher=user)
        newwatch.save()
        newwatch.product.add(prod)
        message = "Added to your WatchList"

    elif ctr == 1:
        newwatch = WatchList.objects.get(watcher=user)
        if prod in newwatch.product.all():
            newwatch.product.remove(prod)
            message = "Removed from WatchList"
        else:
            newwatch.product.add(prod)
            message = "Added to WatchList"

    items = newwatch.product.all()
                

    return render(request, "auctions/watchlist.html", {
        "listings": items,
        "message": message
        })


def categories(request):

    categories = []
    for prod in AuctionListing.objects.filter(active=True):
        categories.append(prod.category)
    return render(request, "auctions/category.html", {
        "categories": set(categories)
        })


def category(request, category):

    listings = AuctionListing.objects.filter(category=category)
    return render(request, "auctions/index.html", {
        "listings": listings
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
