from django import forms

class VideoForm(forms.Form):

    #name = forms.CharField(max_length=255)
    video = forms.FileField()