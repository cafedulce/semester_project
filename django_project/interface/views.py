from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse

from interface.forms import VideoForm
from interface.models import VideoFile

# Create your views here.

def home(request):
    #provisory
    text = """<h1>Django Project homepage</h1>
                <p> hello </p>"""

    return HttpResponse(text)

def upload(request):

    uploaded=False
    form = VideoForm(request.POST or None, request.FILES)

    if form.is_valid():
        video_file = VideoFile()
        video_file.video = form.cleaned_data["video"]
        video_file.name = form.cleaned_data["name"]
        video_file.save()
        uploaded=True

    return render(request, 'interface/upload.html', {'form': form, 'uploaded': uploaded})