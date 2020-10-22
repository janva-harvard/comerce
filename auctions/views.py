from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from .models import User, AuctionListing, Bid, Category
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
            if(amount > highest_bid()['amount__max']):
                new_highest_bid = Bid(
                    amount=amount, for_listing=listing, bidder=user)
                new_highest_bid.save()
                # should check wether logged in or not as well
            # check if this is higher than highest bid so far
            # if so push to db
            # else show warning
    viewed_listing = AuctionListing.objects.get(pk=id)
    print(viewed_listing.watchers.all())
    print("-------------")
    print(User.objects.get(pk=request.user.id))
    print(User.objects.get(pk=request.user.id)
          in viewed_listing.watchers.all())
    return render(request,
                  "auctions/listing.html",
                  {"listing": viewed_listing,
                   "highest_bid": highest_bid()['amount__max'],
                   "form": BidForm(),
                   "is_watched": User.objects.get(pk=request.user.id)
                   in viewed_listing.watchers.all()})


def watchlist_view(request, id):
    usr = User.objects.get(pk=id)
    watchlsts = usr.watched_listings.all()

    if request.method == "POST":
        watched_listing = AuctionListing.objects.get(
            pk=request.POST["lst_id"])
        # if not already watch add user to wathcers in listing
        if request.POST["already_watched"] == 'True':
            user_watching = User.objects.get(pk=request.user.id)
            watched_listing.watchers.remove(user_watching)
        else:
            user_watching = User.objects.get(pk=request.user.id)
            watched_listing.watchers.add(user_watching)
            print(user_watching)
            print(watched_listing)
            print(watched_listing.watchers.all())
            watched_listing.save()
            # id_of_lst_to_watch = request.POST["lst_id"]
            # listing_to_watch = AuctionListing.objects.get(pk=id_of_lst_to_watch)
            # # Hmm can i found out if when this commes back  so i can warn
            # obj = WatchList.objects.get_or_create(
            #     watcher=usr, listing=listing_to_watch
            # )
            # if (obj[1]):
            #     print("created new obj")

    return render(request, "auctions/watchlist.html", {
        "listings": watchlsts
    })


def categories_view(request):
    return render(request,
                  "auctions/categories.html",
                  {
                      "categories": Category.objects.all()
                  })


@ login_required
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
