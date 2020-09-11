from django import forms
from django.forms import ModelForm

from django.forms.widgets import FileInput

from .models import Listing,Bid,Comment

#style-parameters
style = 'form-control w-75'


class ListingForm(ModelForm):
    
    class Meta:
        model = Listing
        exclude = ['listing_image_file','listing_owner','is_active','current_bid']
        widgets = {
             
            
            'listing_title': forms.TextInput(attrs={'class': style,'placeholder':'Title...'}),
            
            'listing_description': forms.Textarea(attrs={'class': style,'placeholder':'Descripion...'}),
            
            'listing_image_url': forms.TextInput(attrs={'class': style, 'placeholder': 'Enter image url...'}),
            
           
            
        }
        
class BidForm(ModelForm):
    
    class Meta:
        model = Bid
        exclude = ['bidder','listing']
        widgets = {
            'bid_field': forms.NumberInput(attrs={'label':'',
                'class':'form-control w-75','style':'inline-block', 'size':'20'
            })
            
        }
        
class CommentForm(ModelForm):
    
    class Meta:
        model = Comment
        exclude = ['listing','comment_user']
        widgets = {
            'comment_field': forms.Textarea(attrs={'class':'form-control w-50','style':'max-height:100px;max-width:350px','placeholder':'Write a comment...','label':''})
        }