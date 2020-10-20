from django.contrib.auth.models import AbstractUser
from django.db import models


#  listing1 = Auction_listing(title="item", description="some item desceription",
#   starting_bid=10.00, image_url="http://test.com", active=True, owner= user1)
# user1 = User()

class User(AbstractUser):
    pass


class Category (models.Model):
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name


class AuctionListing(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    starting_bid = models.DecimalField(max_digits=5, decimal_places=2)
    image_url = models.URLField(max_length=200, blank=True, default=None)
    active = models.BooleanField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,
                                 blank=True,
                                 default=None,
                                 related_name="listings")


class Bid (models.Model):
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    for_listing = models.ForeignKey(AuctionListing, related_name="bids",
                                    on_delete=models.CASCADE)
    # related_name="bids")
    bidder = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bidders")

# hmm would maybe be nicer with a many-to-many in user but
# then i get circlur dependency between AuctionListing and user
# and need a make one off them know to the other before decalaring
# actual class


class WatchList (models.Model):
    watcher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="watchlists")
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)

# class Comment(models.Model):
#     """
#     docstring
#     """
#     pass
