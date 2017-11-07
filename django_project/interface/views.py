from __future__ import unicode_literals

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse

from interface.forms import VideoForm
from interface.models import VideoFile
from interface.models import PySceneDetectArgs

from interface.scripts import *

import scenedetect
import csv

# Create your views here.

media_path = "/media/video_files/"
project_path = "/home/dulce/semester_project/django_project"

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

        video_file, scenedetect_object = form_cleaner(form, media_path, project_path)

        scene_detectors = scenedetect.detectors.get_available()

        sc_man = scenedetect.manager.SceneManager(scenedetect_object, scene_detectors)

        fps, read, processed = scenedetect.detect_scenes_file(path=video_file.absolute_path, scene_manager=sc_man)

        output_file(sc_man, scenedetect_object.output_file ,fps, read)

        """list = splitter(video_file.absolute_path, sc_man.scene_list,project_path,media_path+'cut', sc_man.frame_skip, read)"""
        """number = split_input_video(video_file.absolute_path, media_path+'split', sc_man, fps)"""
        list = ffmpeg_split(project_path,media_path, sc_man.scene_list, video_file.name, 'cut', fps, read)
        print(list)
        return render(request, 'interface/result.html',{'fps':fps,'read':read, 'processed':processed, 'scene_manager':sc_man, 'path':video_file.path, 'list':list})

    return render(request, 'interface/upload.html', {'form': form, 'uploaded': uploaded, 'fps':fps,'read':read, 'processed':processed})

def test(request):

    file = media_path+'concert.mkv'
    return render(request, 'interface/test.html', {'file': file})

def download(request):
    path_to_file = project_path+'/stats_file'
    f = open(path_to_file, 'r')
    response = HttpResponse(f, content_type='application/csv')
    """response['Content-Disposition'] = 'attachment; filename=filename'"""
    return response