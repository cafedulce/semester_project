from django import forms
from interface.choices import *

class VideoForm(forms.Form):

    #name = forms.CharField(max_length=255)
    video = forms.FileField(required=True)
    type = forms.ChoiceField(choices=TYPE_CHOICE, widget=forms.Select(), required=False)
    threshold = forms.IntegerField(required=False, initial=30, help_text='choose a value between 0 and 255(default=30)')

    stats_file = forms.BooleanField(required=False, initial=False)
    save_images = forms.BooleanField(required=False, initial=False)
    quiet_mode = forms.BooleanField(required=False, initial=False)

    downscale = forms.IntegerField(required=False)
    frameskip = forms.IntegerField(required=False)

    start_time = forms.TimeField(required=False)
    end_time = forms.TimeField(required=False)
    duration = forms.TimeField(required=False)

