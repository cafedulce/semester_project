import cv2
import csv
from interface.models import VideoFile
from interface.models import PySceneDetectArgs
from interface.forms import VideoForm

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import os
import sys
import subprocess as sp
from moviepy.tools import subprocess_call
from operator import truediv

import scenedetect
import re

"""def split(capture, output_filename, first_frame, last_frame, fps, size):

    video_writer = cv2.VideoWriter(output_filename, cv2.VideoWriter_fourcc('H','2','6','4'), fps, size)

    if not video_writer.isOpened():
        print('FATAL ERROR - could not open video writer')

    capture.set(cv2.CAP_PROP_POS_FRAMES, first_frame)

    number_of_frames = last_frame-first_frame+1

    while number_of_frames >= 0:
        ret, im = capture.read()
        video_writer.write(im)
        number_of_frames -=1

    return 1

def splitter(filename, scene_list, project_path, output_prefix, frameskip, read):

    name_list = []

    capture = cv2.VideoCapture(filename)

    if not capture.isOpened():
        print('FATAL ERROR - could not open video')
        return -1

    fps = capture.get(cv2.CAP_PROP_FPS)
    ret, image = capture.read()
    if not ret:
        print('capure.read() didnt work')
        return -1
    h, w, c = image.shape
    size = (w,h)
    print scene_list
    scene_list.append(read)
    print scene_list

    begin_frame = 0
    for frame in scene_list:
        name = output_prefix+str(begin_frame)+'.mp4'
        name_list.append(name)
        split(capture, project_path+name, begin_frame, frame-(2+frameskip), fps, size)
        begin_frame = frame

    return name_list"""

def form_cleaner(form, media_path, project_path):

    video_file = VideoFile()
    video_file.video = form.cleaned_data["video"]
    video_file.name = video_file.video_name()
    video_file.path = media_path + video_file.name
    video_file.absolute_path = project_path + video_file.path
    # video_file.absolute_path = video_file.video.path
    video_file.save()

    scenedetect_object = PySceneDetectArgs()
    scenedetect_object.name = video_file.absolute_path
    scenedetect_object.detection_method = form.cleaned_data["type"]
    if form.cleaned_data["threshold"]:
        scenedetect_object.threshold = form.cleaned_data["threshold"]
    #scenedetect_object.frame_skip = form.cleaned_data["frameskip"]
    if form.cleaned_data["downscale"]:
        scenedetect_object.downscale_factor = form.cleaned_data["downscale"]

    if form.cleaned_data["stats_file"]:
        stat = open('stats_file', 'w')
        scenedetect_object.stats_file = stat

    if form.cleaned_data["output_file"]:
        out = open('scenes', 'w')
        scenedetect_object.output_file = out

    return video_file, scenedetect_object


### code from PySceneDetect
def output_file(smgr, file, video_fps, frames_read):

    scene_list_msec = [(1000.0 * x) / float(video_fps) for x in smgr.scene_list]
    scene_list_tc = [scenedetect.timecodes.get_string(x) for x in scene_list_msec]
    # Create new lists with scene cuts in seconds, and the length of each scene.
    scene_start_sec = [(1.0 * x) / float(video_fps) for x in smgr.scene_list]
    scene_len_sec = []
    if len(smgr.scene_list) > 0:
        scene_len_sec = smgr.scene_list + [frames_read]
        scene_len_sec = [(1.0 * x) / float(video_fps) for x in scene_len_sec]
        scene_len_sec = [(y - x) for x, y in zip(scene_len_sec[:-1], scene_len_sec[1:])]

    scenedetect.output_scene_list(file, smgr, scene_list_tc,
                      scene_start_sec, scene_len_sec)

    file.close()

"""def split_input_video(input_path, output_path, smgr, video_fps):

    scene_list_msec = [(1000.0 * x) / float(video_fps) for x in smgr.scene_list]
    scene_list_tc = [scenedetect.timecodes.get_string(x) for x in scene_list_msec]
    timecode_list_str = ','.join(scene_list_tc)
    
    #args.output.close()
    print('[PySceneDetect] Splitting video into clips...')
    ret_val = None
    number=0
    try:
        ret_val = subprocess.call(
            ['mkvmerge',
             '-o', output_path,
             '--split', 'timecodes:%s' % timecode_list_str,
             input_path])
        number+=1
    except FileNotFoundError:
        print('[PySceneDetect] Error: mkvmerge could not be found on the system.'
              ' Please install mkvmerge to enable video output support.')
    if ret_val is not None:
        if ret_val != 0:
            print('[PySceneDetect] Error splitting video '
                  '(mkvmerge returned %d).' % ret_val)
        else:
            print('[PySceneDetect] Finished writing scenes to output.')

    return number"""

def ffmpeg_split(project_path, media_path, list, filename, output_name, output_format, fps, read):

    #convert mkv file to mp4
    input_name = project_path+media_path+'converted.mp4'
    cmd = ["ffmpeg","-i",project_path+media_path+filename,"-c:v","copy","-an","-y",input_name]
    subprocess_call(cmd)
    #input_name = project_path+media_path+filename

    list.append(read)
    media_name_list = []

    begin = 0
    for current in list:
        t2 = current-begin
        t1 = frames_to_second(begin, fps)
        print('start time :', t1)
        t2 = frames_to_second(t2, fps)
        print('stop time :', t2)
        tar=media_path+output_name+str(begin)+output_format
        media_name_list.append(tar)
        tar = project_path+tar
        #ffmpeg_extract_subclip(file_path+filename, t1, t2, output_name,name=tar)
        #cmd = ["ffmpeg","-ss",str(t1),"-i",project_path+media_path+filename,"-t",str(t2),"-codec","copy","-copyts",tar]
        #cmd = ["ffmpeg", "-i", project_path+media_path+filename, "-ss", str(t1), "-strict", "-2", "-t", str(t2), tar]
        cmd = ["ffmpeg","-i",input_name,"-c:av","copy","-ss",str(t1),"-t",str(t2),"-y",tar]
        subprocess_call(cmd)

        begin = current

    return media_name_list

"""def convert_seconds_to_timeformat(a):
    minute, second = divmod(a, 60)
    hour, minute = divmod(minute, 60)
    return str(hour)+str(minute)+str(second)"""

"""def frames_to_timecode(frames, fps):
    frame = int(frames)
    return '{0:02d}:{1:02d}:{2:02d}.{3:02d}'.format(int(frame // (3600*fps)), int(frame // (60*fps))%60, int(frame // fps)%60 , int(frame % fps))"""

def frames_to_second(frames, fps):
    return truediv(frames, fps)

def combine(video_list, to_combine_list, project_path, media_path):
    print(video_list)
    print(to_combine_list)
    while len(to_combine_list) >= 2:
        indexa = video_list.index(to_combine_list[0])
        indexb = video_list.index(to_combine_list[1])
        if abs(indexa-indexb) > 1:
            to_combine_list.pop(0)
        else:
            a = project_path+to_combine_list[0]
            b = project_path+to_combine_list[1]
            #regex
            num1 = re.search('shot([0-9]+)\.', a).group(1)
            num2 = re.search('shot([0-9]+)\.', b).group(1)
            o = media_path+"shot"+str(num1)+str(num2)+".mp4"

            arg = '[0:v:0] [1:v:0] concat=n=2:v=1 [v]'
            cmd = ["ffmpeg","-i",a,"-i",b,"-filter_complex",arg,"-map","[v]","-y",project_path+o]
            subprocess_call(cmd)
            video_list.pop(indexb)
            video_list.pop(indexa)
            video_list.insert(indexa, o)
            to_combine_list.pop(0)
            to_combine_list.pop(0)
            to_combine_list.insert(0, o)
    return video_list