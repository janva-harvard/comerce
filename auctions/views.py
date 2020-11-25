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
    winners = None
    if(request.user.id):
        winners = AuctionListing.objects.filter(buyer=request.user.id)

    print(AuctionListing.objects.filter(buyer=request.user.id))
    return render(request,
                  "auctions/index.html",
                  {
                      "listings": AuctionListing.objects.filter(active=True),
                      # filter by auctions  won by this current user
                      "won_auctions": winners
                  })


def category_listing_view(request, id):
    category = Category.objects.get(pk=id)
    return render(request,
                  "auctions/category_listing.html",
                  {"listings": category.listings.all()})


def highest_bid_for(listing):
    # TODO could I possably use get_or_create here
    bids = listing.bids
    if not bids.all():
        return Bid(amount=listing.starting_bid,
                   for_listing=listing,
                   bidder=listing.owner)
    else:
        return bids.all().order_by('-amount')[0]


def inactivate_listing(listing):
    listing.active = False


def announce_winner(listing):
    highest_bid = highest_bid_for(listing)
    listing.buyer = highest_bid.bidder


def store_to_db(model_obj):
    model_obj.save()


def close_auction(listing):
    # hmm could inline variable but would mean extra requests to db
    inactivate_listing(listing)
    announce_winner(listing)
    store_to_db(listing)


def biding_against_myself(user_bidding, highest_bid):
    return user_bidding.id == highest_bid.bidder.id


def make_bid(request, id):
    # hmm maybe wrong level of abstraction
    error_msg = None
    posted_form = BidForm(request.POST)
    if posted_form.is_valid():
        # if BidForm(request.POST).is_valid():
        user_making_bid = User.objects.get(pk=request.user.id)
        listing_to_buy = AuctionListing.objects.get(pk=id)
        bid_made_by_user = posted_form.cleaned_data["amount"]
        highest_bid = highest_bid_for(listing_to_buy)
        print("bidding ")
        # Do we already hold the highest bid
        # if highest_bid.bidder.id == user_making_bid.id:
        if biding_against_myself(user_making_bid, highest_bid):
            error_msg = "You allready hold the highest bid"
            return error_msg

        # is_highest_bid?
        if bid_made_by_user < highest_bid.amount:
            error_msg = "You cannot underbid"
            return error_msg

        # Store new highest bid to DB
        Bid(amount=bid_made_by_user,
            for_listing=listing_to_buy,
            bidder=user_making_bid).save()

        # TODO need a better solution don't want to pass around error msg
        # catch throw
        return error_msg


def is_post_request(request):
    return request.method == "POST"


def is_close_request(request):
    return 'closeauction' in request.POST


def listing_view(request, id):
    error_msg = None
    if is_post_request(request):
        # A bit contrieved way of doing things
        if is_close_request(request):
            # TODO refector getting object from request function
            close_auction(listing=AuctionListing.objects.get(
                pk=request.POST['lst_id']))
        else:
            error_msg = make_bid(request, id)

    # TODO: Hmm making annother query for same entity again, necessary?
    # TODO  not balanced
    viewed_listing = AuctionListing.objects.get(pk=id)
    return render(request,
                  "auctions/listing.html",
                  {"listing": viewed_listing,
                   # TODO  same thing here
                   "highest_bid": highest_bid_for(viewed_listing),
                   "form": BidForm(),
                   "is_watched": request.user.id and
                   User.objects.get(pk=request.user.id)
                   in viewed_listing.watchers.all(),
                   "error_msg": error_msg,
                   })


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

    return render(request, "auctions/watchlist.html", {
        "listings": watchlsts,
                  "won_auctions":
                      AuctionListing.objects.filter(buyer=request.user.id)

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

############################# implemented  before #############################


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
