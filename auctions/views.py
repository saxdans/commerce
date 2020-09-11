from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required


from .models import User,Listing,categories_list,Bid,Comment,WatchList
from .forms import ListingForm,BidForm,CommentForm


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
            return render(request, "auctions/register.html", 
                {
                "message": "Username already taken."
                 })
        new_wl = WatchList.objects.create(wluser=user)
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

    
def index(request):
    username = ''
    if User.objects.filter(pk=request.user.id).exists:
        username = request.user
    return render(request, "auctions/list.html",
    {'block_title':'Active Listings',
     'headline':'Active Listings',
    'listings': Listing.objects.filter(is_active=True),
     'username':username
     
     })
    
def closedlistings(request):
    username = ''
    if User.objects.filter(pk=request.user.id).exists:
        username = request.user
    
    return render(request, "auctions/list.html",
    {'block_title':'Closed Listings',
     'headline':'Closed Listings',
    'listings': Listing.objects.filter(is_active=False),
     'username':username
     })

def categories(request):
    choices = categories_list()
    return render(request,"auctions/categories.html", {
        'categories':choices 
        })

def categorylist(request,category):
    empty=False
    listings = Listing.objects.filter(listing_category=category,is_active=True)
    if not listings:
        empty=True
    return render(request,"auctions/list.html",
                  {
        'block_title':category,
        'headline': category,
        'listings':listings,
        'category': category,
        'empty': empty })
    

@login_required(login_url = 'login')
def newlisting(request):
    user = User.objects.get(pk=request.user.id)
    
    
    invalid_bid_message = ''
    if request.method == 'POST':
        
        form = ListingForm(request.POST)
        bidform = BidForm(request.POST)
        bidform.fields['bid_field'].widget.attrs.update({'placeholder':'Enter starting bid...'})
        if form.is_valid() and bidform.is_valid():
            new_bid = bidform.save(commit=False)
            
            try:
                new_bid.save()
            except IntegrityError:
                invalid_bid_message = 'Must be at least 0'
                return render(request,'auctions/newlisting.html',{
                    'form': form,
                    'bidform':bidform,
                    'invalid_bid_message':invalid_bid_message
                })
            new_listing = form.save(commit=False)
            new_listing.listing_owner = user
            new_listing.save()
            
            
            new_bid.bidder = user
            new_bid.listing = new_listing
            new_bid.save()
            
            new_listing.current_bid = new_bid.bid_field
            new_listing.save()
            
            return HttpResponseRedirect(reverse('viewlisting', kwargs={'listing_title': new_listing.listing_title}))
        
    bidform=BidForm()
    bidform.fields['bid_field'].widget.attrs.update({'placeholder':'Enter starting bid...'})
    
    return render(request,'auctions/newlisting.html',
                  {
        'form':ListingForm(),
        'bidform':bidform,
        'invalid_bid_message':invalid_bid_message
        })

def viewlisting(request,listing_title):
    if Listing.objects.filter(listing_title=listing_title):
        listing = Listing.objects.filter(listing_title=listing_title).last()
        if request.POST.get('fromlistpage'):
            listing = Listing.objects.get(pk=request.POST.get('fromlistpage'))
        listing_title = listing.listing_title
        
        bidform=BidForm(request.POST or None)
        bidform.fields['bid_field'].widget.attrs.update({'placeholder':'Place bid...'})
        invalid_bid_message = ''
       
        comments = Comment.objects.filter(listing_id=listing.id)
        current_bid = Bid.objects.filter(listing_id=listing.id).last().bid_field
        bidder = listing.bidlisting.last().bidder
        
        if bidder == request.user:
            bidder = 'you'
        
        winner = False
        nowinner = False
        
        is_first_bid = True
        
        is_active = listing.is_active
        print(is_active)
        
        
        if Bid.objects.filter(listing_id=listing.id).count() > 1:
            is_first_bid = False
        
        on_wl = False

        if User.objects.filter(pk=request.user.id).exists():
            
            if not listing.is_active and is_first_bid:
                nowinner = True
            elif (not listing.is_active) and (Bid.objects.filter(listing=listing).last().bidder ==request.user):
                print('win')
                winner = True
            
            if not WatchList.objects.filter(wluser=request.user,listing=listing).exists():
                wl = WatchList.objects.create(wluser=request.user,listing=listing)
                
            on_wl = listing.wlistings.filter(wluser=request.user,listing=listing).last().on_watchlist
            
            if request.POST.get('bidOK'):

                new_bidform = BidForm(request.POST)
                if new_bidform.is_valid():
                    new_bid = new_bidform.save(commit=False)
                    if (is_first_bid and new_bid.bid_field >= current_bid) or (not is_first_bid and new_bid.bid_field > current_bid):
                        if new_bid.bid_field >= current_bid:
                            new_bid.listing = listing
                            new_bid.bidder = request.user
                            new_bid.save()
                            listing.current_bid = Bid.objects.last().bid_field
                            listing.save()
                            bidder = listing.bidlisting.last().bidder 
                            
                            return HttpResponseRedirect(reverse('viewlisting',kwargs={'listing_title':listing_title}))
                    else:
                        invalid_bid_message = 'Bid is too low'
                        
                   
            if request.POST.get('comment'):

                new_cf = CommentForm(request.POST)
                if new_cf.is_valid():
                    new_comment = new_cf.save(commit=False)
                    new_comment.listing = listing
                    new_comment.comment_user = request.user
                    new_comment.save()
                    comments = Comment.objects.filter(listing_id=listing.id)
                    return HttpResponseRedirect(reverse('viewlisting',kwargs={'listing_title':listing_title}))

            if request.POST.get('watchlist'):
                wl = listing.wlistings.get(listing=listing,wluser=request.user)
                if wl.on_watchlist:
                    wl.on_watchlist = False
                    wl.save()
                    on_wl = False
                else:
                    wl.on_watchlist=True
                    wl.save()
                    on_wl = True


            if request.POST.get('closebidding'):
                WatchList.objects.filter(listing=listing).delete()
                listing.is_active = False
                listing.save()

                return HttpResponseRedirect(reverse('closedlistings'))
        
        
        elif request.method == 'POST' and not User.objects.filter(pk=request.user.id).exists():
            if request.POST.get('fromlistpage'):
                pass
            else:
                return HttpResponseRedirect(reverse('login'))
            
        return render(request, 'auctions/viewlisting.html',
                          {'block_title':listing_title,
                           'headline':listing_title,
                            'listing_title': listing_title,
                           'listing': listing,
                           'bidform':bidform,
                           'current_bid':listing.current_bid,
                            'commentform':CommentForm(),
                            'comments':comments,
                            'username':request.user,
                           'bidder':bidder,
                           'on_wl':on_wl,
                           'invalid_bid_message':invalid_bid_message,
                           'is_first_bid':is_first_bid,
                           'winner':winner,
                           'nowinner':nowinner,
                           'is_active':is_active
            })



   
    return HttpResponseRedirect(reverse('nosuchpage'))
    
@login_required(login_url = 'login')
def mylistings(request):
    user = User.objects.get(pk=request.user.id)
    userlistings = request.user.userlistings.all()
    
    return render(request, 'auctions/list.html',
                  { 'block_title':'My Listings',
                    'headline': 'My listings',
                    'listings':userlistings})


@login_required(login_url = 'login')
def watchlist(request):
    user = User.objects.get(pk=request.user.id)
    watchlist = WatchList.objects.filter(wluser_id=user.id,on_watchlist=True)
    listings_ids = watchlist.values('listing_id')
    listings = Listing.objects.filter(pk__in=listings_ids)
    
    return render(request,'auctions/list.html',
                 {  'block_title':'Watchlist',
                    'headline':'Watchlist',
                     'listings':listings
                 }
                 )

def nosuchpage(request):
    return render(request, 'auctions/nosuchpage.html')
    