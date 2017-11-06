from django import forms
from interface.choices import *

class VideoForm(forms.Form):

    #name = forms.CharField(max_length=255)
    video = forms.FileField(required=True)
    type = forms.ChoiceField(choices=TYPE_CHOICE, widget=forms.Select(), required=False)
    threshold = forms.IntegerField(required=False, initial=30 ,help_text='(default=30)')

    stats_file = forms.BooleanField(required=False, initial=False)
    output_file = forms.BooleanField(required=False, initial=False)
    #save_images = forms.BooleanField(required=False, initial=False)
    #quiet_mode = forms.BooleanField(required=False, initial=False)

    downscale = forms.IntegerField(required=False, initial=5, help_text='(default=5)')
    #frameskip = forms.IntegerField(required=False, initial=2)

    #start_time = forms.TimeField(required=False)
    #end_time = forms.TimeField(required=False)
    #duration = forms.TimeField(required=False)

