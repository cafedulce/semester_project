from django import forms
from interface.choices import *



class VideoForm(forms.Form):

    #here is the form we need in the home page
    #the user can choose the content or threshold algorithm, the threshold, and the downscale factor
    #the framskip is left as comment because it lead to many errors

    video = forms.FileField(required=True)
    type = forms.ChoiceField(choices=TYPE_CHOICE, widget=forms.Select(), required=False)
    threshold = forms.IntegerField(required=False, initial=30 ,help_text='(default=30)')
    downscale = forms.IntegerField(required=False, initial=5, help_text='(default=5)')
    #frameskip = forms.IntegerField(required=False, initial=2)

