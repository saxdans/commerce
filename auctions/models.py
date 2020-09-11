from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.files import File
from urllib.request import urlopen
from tempfile import NamedTemporaryFile
import os

categories_vars = [('Decoration','DECORATION'), ('Electronics','ELECTRONICS'), ('Sports','SPORTS'),('Music gear','MUSIC GEAR'), ('Home','HOME'), ('Other','OTHER')]

def categories_list():
    return categories_vars

class User(AbstractUser):
    pass


    
    
class Listing(models.Model):
    listing_owner = models.ForeignKey(User,on_delete=models.CASCADE,verbose_name = 'User', related_name='userlistings',null=True)
    listing_title = models.CharField(max_length = 30,verbose_name='')
    listing_description = models.TextField(verbose_name='')
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    listing_image_url = models.URLField(blank=True)
    
    listing_category = models.CharField(max_length=64, choices=categories_list())
    
    is_active = models.BooleanField(default=True)
    current_bid = models.IntegerField(null=True)
    
   
    
    def __str__(self):
        return f"{self.listing_title} by {self.listing_owner}"
    
class Bid(models.Model):
    last_modified = models.DateTimeField(auto_now=True)
    time_of_bid = models.DateTimeField(auto_now_add=True)
    bid_field = models.IntegerField(blank=True,null=True,verbose_name='')
    bidder = models.ForeignKey(User,on_delete=models.CASCADE,related_name='biduser',null=True)
    listing = models.ForeignKey(Listing,on_delete=models.CASCADE,related_name='bidlisting',null=True)
    def __str__(self):
        return f'{self.bidder} on {self.listing} at {self.time_of_bid}'

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(bid_field__gte=0),
            name='gt_0'),
                                   ]
    
class Comment(models.Model):
    time_posted = models.DateTimeField(auto_now=True)
    comment_field = models.TextField(blank=True,verbose_name='')
    listing = models.ForeignKey(Listing,on_delete=models.CASCADE,related_name='commentlisting')
    comment_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='commentuser')
    
    def __str__(self):
        return f'{self.comment_user} on {self.listing}'

class WatchList(models.Model):
    on_watchlist = models.BooleanField(default=False)
    listing = models.ForeignKey(Listing,on_delete=models.CASCADE,related_name='wlistings')
    wluser = models.ForeignKey(User,on_delete=models.CASCADE,related_name='wluser')
    
    def __str__(self):
        return f'{self.wluser}, {self.listing} on watchlist: {self.on_watchlist}'