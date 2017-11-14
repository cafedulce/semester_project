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
        f_r_p = scenedetect.detect_scenes_file(path=video_file.absolute_path, scene_manager=sc_man)

        output_format = '.mp4'
        output_name = 'shot'
        list = ffmpeg_split(project_path,media_path, sc_man.scene_list, video_file.name, output_name, output_format, f_r_p[0], f_r_p[1])

        request.session['fps_read_proc'] = f_r_p
        request.session['det_thres_down'] = (sc_man.detection_method,sc_man.args.threshold,sc_man.downscale_factor)
        request.session['video_list'] = list
        
        return redirect(result)

    return render(request, 'interface/upload.html', {'form': form, 'uploaded': uploaded, 'fps':fps,'read':read, 'processed':processed})

def result(request):

    frp = request.session.get('fps_read_proc')
    dtd = request.session.get('det_thres_down')
    list = request.session.get('video_list')
    return render(request, 'interface/result.html', {'fps':frp[0],'read':frp[1], 'processed':frp[2], 'det':dtd[0],'thres':dtd[1],'down':dtd[2], 'list':list})

def test(request):
    print(request.session.get('atest'))
    file = project_path+media_path+'goldeneye.mp4'
    return render(request, 'interface/test.html', {'file':file})


def download(request):
    path_to_file = project_path+'/stats_file'
    f = open(path_to_file, 'r')
    response = HttpResponse(f, content_type='application/csv')
    """response['Content-Disposition'] = 'attachment; filename=filename'"""
    return response