from django.contrib import admin
from .models import AuctionListing, Bid, User, WatchList

# Register your models here.
admin.site.register(AuctionListing)
admin.site.register(Bid)
admin.site.register(User)
admin.site.register(WatchList)
