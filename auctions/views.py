from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from .models import User, AuctionListing, Bid, WatchList, Category
from .forms import NewListingsForm, BidForm


def index(request):
    active_listings = AuctionListing.objects.filter(active=True)
    return render(request,
                  "auctions/index.html", {
                      "listings": active_listings,
                  })


def category_listing_view(request, id):
    category = Category.objects.get(pk=id)
    return render(request,
                  "auctions/category_listing.html",
                  {"listings": category.listings.all()})


def highest_bid():
    # needt to make shore that there are existing bids
    return Bid.objects.aggregate(Max('amount'))


def listing_view(request, id):
    if request.method == "POST":

        posted_form = BidForm(request.POST)
        if posted_form.is_valid():
            user = User.objects.get(pk=request.user.id)
            listing = AuctionListing.objects.get(pk=id)
            amount = posted_form.cleaned_data["amount"]
            print(highest_bid())
            if(amount > highest_bid()['amount__max']):
                new_highest_bid = Bid(
                    amount=amount, for_listing=listing, bidder=user)
                new_highest_bid.save()
                # should check wether logged in or not as well
            # check if this is higher than highest bid so far
            # if so push to db
            # else show warning
    return render(request,
                  "auctions/listing.html",
                  {"listing": AuctionListing.objects.get(pk=id),
                   "highest_bid": highest_bid()['amount__max'],
                   "form": BidForm()})


def watchlist_view(request, id):
    return render(request, "auctions/watchlist.html", {})
    pass


def categories_view(request):

    return render(request,
                  "auctions/categories.html",
                  {
                      "categories": Category.objects.all()
                  })


@login_required
def new_listing_view(request):
    if request.user.is_authenticated and not request.user.is_anonymous:
        if request.method == 'POST':
            # refactor later
            # store_post_to_db(request.POST)
            # use cleaned data

            new_listing = AuctionListing(
                title=request.POST['title'],
                description=request.POST['description'],
                starting_bid=request.POST['starting_bid'],
                # Hmm might need to check if this exists or not
                # take happy path for now
                image_url=request.POST['image_url'],
                # active=True if request.POST['active'] == "on" else False,
                active='active' in request.POST,
                owner=request.user,
                category=Category.objects.get(id=request.POST['category']),
            )

            new_listing.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            form = NewListingsForm()
            return render(request,
                          "auctions/new_listing_form.html",
                          {"form": form})
    else:
        return render(request,
                      "auctions/login.html")


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
