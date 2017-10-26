from __future__ import unicode_literals

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse

from interface.forms import VideoForm
from interface.models import VideoFile
from interface.models import PySceneDetectArgs

from interface.scripts import split

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

    media_path = "/media/video_files/"

    if form.is_valid():
        video_file = VideoFile()
        video_file.video = form.cleaned_data["video"]
        video_file.name = video_file.video_name()
        video_file.path = media_path+video_file.name
        video_file.absolute_path = '/home/dulce/semester_project/django_project/'+video_file.path
        #video_file.absolute_path = video_file.video.path
        video_file.save()
        uploaded=True
        #test
        print(video_file.name)
        print(video_file.path)
        print(video_file.absolute_path)

        scenedetect_object = PySceneDetectArgs()
        scenedetect_object.name = video_file.absolute_path
        scenedetect_object.type = 'content'
        scenedetect_object.threshold = 30
        scenedetect_object.save_images = False
        scenedetect_object.quiet_mode = True
        scenedetect_object.stats_file = False
        scenedetect_object.start_time = None
        scenedetect_object.end_time = None
        scenedetect_object.duration = None

        scene_detectors = scenedetect.detectors.get_available()

        sc_man = scenedetect.manager.SceneManager(scenedetect_object, scene_detectors)

        fps, read, processed = scenedetect.detect_scenes_file(path=scenedetect_object.name, scene_manager=sc_man)

        return render(request, 'interface/result.html',{'fps':fps,'read':read, 'processed':processed, 'scene_manager':sc_man, 'path':video_file.path})

    return render(request, 'interface/upload.html', {'form': form, 'uploaded': uploaded, 'fps':fps,'read':read, 'processed':processed})

def test(request):

    split('/home/dulce/semester_project/django_project/media/video_files/goldeneye.mp4', '/home/dulce/semester_project/django_project/media/video_files/cut.mp4', 200, 300)
    path = '/media/video_files/cut.mp4'

    return render(request, 'interface/test.html', {'path': path})