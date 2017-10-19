from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse

from interface_without_scenedetect.forms import VideoForm
from interface_without_scenedetect.models import VideoFile

# Create your views here.

def home(request):
    #provisory
    text = """<h1>salut</h1>
                <p> okok </p>"""

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

    return render(request, 'interface_without_scenedetect/upload.html', {'form': form, 'uploaded': uploaded})