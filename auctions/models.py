from django.contrib.auth.models import AbstractUser
from django.db import models

"""product = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, null=True)
latest_bid = models.ForeignKey(Bid, on_delete=models.CASCADE, null=True)"""

class User(AbstractUser):
	pass


class AuctionListing(models.Model):
	title = models.CharField(max_length=64)
	description = models.TextField()
	start_bid = models.IntegerField()
	pic_url = models.URLField(max_length=250, blank=True)
	category = models.CharField(max_length=64, blank=True)
	seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="product", null=True)
	active = models.BooleanField(default=True, blank=True, null=True)
	buyer = models.ForeignKey(User, blank=True, on_delete=models.CASCADE, related_name="won", null=True)
	
	def __str__(self):
		return f"{self.title}(${self.start_bid})"


class Bid(models.Model):
	bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
	product = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bid")
	latest_bid = models.IntegerField(default='startbid')

	def startbid(self):
		self.latest_bid = self.product.start_bid

	def save(self, *args, **kwargs):

		bids = Bid.objects.all()
		for bid in bids:
			if self.product == bid.product:
				if self.latest_bid <= bid.latest_bid:
					raise Exception("lolol")

		if self.product.start_bid>self.latest_bid:
			raise Exception("Your Bid cannot be less than previous bids!")

		super(Bid, self).save(*args, **kwargs)

	def __str__(self):
		return f"${self.latest_bid} by {self.bidder}"


class Comment(models.Model):
	commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter")
	product = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comment")
	comment = models.TextField()

	def __str__(self):
		return f"{self.comment}"


class WatchList(models.Model):
	watcher = models.OneToOneField(User, on_delete=models.CASCADE, related_name="watcher")
	product = models.ManyToManyField(AuctionListing, related_name="watch")

	def __str__(self):
		products = ", ".join(str(prod) for prod in self.product.all())
		return f"{products} for {self.watcher}"
