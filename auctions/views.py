from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, AuctionListing, Bid, WatchList
from .forms import NewListingsForm


def index(request):
    active_listings = AuctionListing.objects.filter(active=True)
    return render(request,
                  "auctions/index.html", {
                      "listings": active_listings
                  })


def new_listing_view(request):
    if request.user.is_authenticated and not request.user.is_anonymous:
        if request.method == 'POST':
            # refactor later
            # store_post_to_db(request.POST)
            new_listing = AuctionListing(
                title=request.POST['title'],
                description=request.POST['description'],
                category=request.category,
                starting_bid=request.POST['starting_bid'],
                # Hmm might need to check if this exists or not
                # take happy path for now
                image_url=request.POST['image_url'],
                active=True if request.POST['active'] == "on" else False,
                owner=request.user,
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
