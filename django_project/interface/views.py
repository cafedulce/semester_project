from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse

from interface.forms import VideoForm
from interface.models import VideoFile
from interface.models import PySceneDetectArgs

import scenedetect

# Create your views here.

def home(request):
    #provisory
    text = """<h1>Django Project homepage</h1>
                <p> hello </p>"""

    return HttpResponse(text)

def upload(request):

    uploaded=False
    form = VideoForm(request.POST or None, request.FILES)

    fps, read, processed = 0,0,0

    if form.is_valid():
        video_file = VideoFile()
        video_file.video = form.cleaned_data["video"]
        video_file.save()
        uploaded=True

        scenedetect_object = PySceneDetectArgs()
        scenedetect_object.name = (video_file.video.path)
        scenedetect_object.type = 'content'
        scenedetect_object.threshold = 30
        scenedetect_object.save_images = False
        scenedetect_object.quiet_mode = True
        scenedetect_object.stats_file = False
        scenedetect_object.start_time = None
        scenedetect_object.end_time = None
        scenedetect_object.duration = None

        scene_detectors = scenedetect.detectors.get_available()

        smgr_content = scenedetect.manager.SceneManager(scenedetect_object, scene_detectors)

        fps, read, processed = scenedetect.detect_scenes_file(path=scenedetect_object.name, scene_manager=smgr_content)


    return render(request, 'interface/upload.html', {'form': form, 'uploaded': uploaded, 'fps':fps,'read':read, 'processed':processed})