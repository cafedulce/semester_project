from __future__ import unicode_literals

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from interface.forms import VideoForm
from interface.models import VideoFile
from interface.models import PySceneDetectArgs
from interface.constants import *
from interface.scripts import *

import scenedetect
import csv

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

        video_file, scenedetect_object = form_cleaner(form)
        scene_detectors = scenedetect.detectors.get_available()
        sc_man = scenedetect.manager.SceneManager(scenedetect_object, scene_detectors)
        f_r_p = scenedetect.detect_scenes_file(path=video_file.absolute_path, scene_manager=sc_man)
        #adding the frist frame (not taken in account in pySceneDetect)
        sc_man.scene_list.insert(0, 0)

        output_file(sc_man.scene_list, scenedetect_object.output_file, f_r_p[0], f_r_p[1])

        video_list = ffmpeg_split(sc_man.scene_list, video_file.name, f_r_p[0], f_r_p[1])

        request.session['fps_read_proc'] = f_r_p
        request.session['det_thres_down'] = (sc_man.detection_method,sc_man.args.threshold,sc_man.downscale_factor)
        request.session['video_list'] = video_list
        request.session['scene_list'] = sc_man.scene_list

        return redirect(result)

    return render(request, 'interface/upload.html', {'form': form, 'uploaded': uploaded, 'fps':fps,'read':read, 'processed':processed})

def result(request):

    frp = request.session.get('fps_read_proc')
    dtd = request.session.get('det_thres_down')
    video_list = request.session.get('video_list')
    scene_list = request.session.get('scene_list')
    print(scene_list)

    type = request.POST.get('type')
    if type == 'combine':
        to_combine = request.POST.getlist('combine[]')
        if to_combine:
            video_list = combine(scene_list, video_list, to_combine,frp[0],frp[1])
            request.session['video_list'] = video_list
            return redirect(result)
    elif type == 'cut':
        vid = int(request.POST.get('v'))
        time = float(request.POST.get('t'))
        if not time == 0:
            video_list = cut(scene_list, video_list, vid, time,frp[0],frp[1])
            request.session['video_list'] = video_list
            return redirect(result)

    return render(request, 'interface/result.html', {'fps':frp[0],'read':frp[1], 'processed':frp[2], 'det':dtd[0],'thres':dtd[1],'down':dtd[2], 'vlist':video_list,'size': range(len(video_list))})

def test(request):
    file = video_path+'goldeneye.mp4'
    time = 0
    count = 0
    """if request.method == 'POST':
        print(request.POST)
        if 'var' in request.POST:
            time = request.POST['var']
            return HttpResponse('success')
        return HttpResponse('fail')"""
    t = request.POST.getlist('cut[]')
    c = request.POST.getlist('count')
    if t:
        time = t
    if c:
        count = c
    print(time)
    print(count)
    print(request.POST)
    return render(request, 'interface/test.html', {'file':file})


def download(request):
    path_to_file = project_path+'/stats_file'
    f = open(path_to_file, 'r')
    response = HttpResponse(f, content_type='application/csv')
    """response['Content-Disposition'] = 'attachment; filename=filename'"""
    return response