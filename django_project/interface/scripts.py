import cv2
import csv
from interface.models import VideoFile
from interface.models import PySceneDetectArgs
from interface.forms import VideoForm
from interface.constants import *

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import os
import sys
import subprocess as sp
from moviepy.tools import subprocess_call
from operator import truediv

import scenedetect
import re
import csv

def form_cleaner(form):

    video_file = VideoFile()
    video_file.video = form.cleaned_data["video"]
    video_file.name = video_file.video_name()
    video_file.path = video_path + video_file.name
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

    stat = open(doc_path+statfile_name, 'w')
    scenedetect_object.stats_file = stat

    out = open(doc_path+scenes_name, 'w')
    scenedetect_object.output_file = out

    return video_file, scenedetect_object


### code from PySceneDetect
def output_file(scene_list, file, video_fps, frames_read):

    scene_list_msec = [(1000.0 * x) / float(video_fps) for x in scene_list]
    scene_list_tc = [scenedetect.timecodes.get_string(x) for x in scene_list_msec]
    # Create new lists with scene cuts in seconds, and the length of each scene.
    scene_start_sec = [(1.0 * x) / float(video_fps) for x in scene_list]
    scene_len_sec = []
    if len(scene_list) > 0:
        scene_len_sec = scene_list + [frames_read]
        scene_len_sec = [(1.0 * x) / float(video_fps) for x in scene_len_sec]
        scene_len_sec = [(y - x) for x, y in zip(scene_len_sec[:-1], scene_len_sec[1:])]

    output_scene_list(file, scene_list, scene_list_tc,
                      scene_start_sec, scene_len_sec)

    file.close()

def output_scene_list(csv_file, scene_list, scene_list_tc, scene_start_sec,
                      scene_len_sec):
    ''' Outputs the list of scenes in human-readable format to a CSV file
        for further analysis. '''
    # Output timecodes to CSV file if required (and scenes were found).
    #if args.output and len(scene_list) > 0:
    if csv_file and len(scene_list) > 0:
        csv_writer = csv.writer(csv_file) #args.output)
        # Output timecode scene list
        csv_writer.writerow(scene_list_tc)
        # Output detailed, human-readable scene list.
        csv_writer.writerow(["Scene Number", "Frame Number (Start)",
                             "Timecode", "Start Time (seconds)", "Length (seconds)"])
        for i, _ in enumerate(scene_list):
            csv_writer.writerow([str(i+1), str(scene_list[i]),scene_list_tc[i], str(scene_start_sec[i]),str(scene_len_sec[i])])


def ffmpeg_split(list, filename, fps, read):

    #convert mkv file to mp4
    input_name = project_path+video_path+video_target_temp+video_target_format
    cmd = ["ffmpeg","-i",project_path+video_path+filename,"-c:v","copy","-an","-y",input_name]
    subprocess_call(cmd)
    #input_name = project_path+video_path+filename

    # discard first scene(0) and add last read for computing purpose/ at the end add/remove these elements
    list.pop(0)
    list.append(read)
    media_name_list = []

    begin = 0
    for current in list:
        t2 = current-begin
        t1 = frames_to_second(begin, fps)
        t2 = frames_to_second(t2, fps)
        tar= video_path+video_target_name+str(begin)+video_target_format
        media_name_list.append(tar)
        tar = project_path+tar
        #ffmpeg_extract_subclip(file_path+filename, t1, t2, output_name,name=tar)
        #cmd = ["ffmpeg","-ss",str(t1),"-i",project_path+video_path+filename,"-t",str(t2),"-codec","copy","-copyts",tar]
        #cmd = ["ffmpeg", "-i", project_path+video_path+filename, "-ss", str(t1), "-strict", "-2", "-t", str(t2), tar]
        cmd = ["ffmpeg","-i",input_name,"-c:av","copy","-ss",str(t1),"-t",str(t2),"-y",tar]
        subprocess_call(cmd)

        begin = current
    list.pop(-1)
    list.insert(0,0)

    return media_name_list

def frames_to_second(frames, fps):
    return truediv(frames, fps)
def seconds_to_frame(sec, fps):
    return int(sec*fps)

def combine(scene_list, video_list, to_combine_list, fps, read):
    while len(to_combine_list) >= 2:
        index1 = video_list.index(to_combine_list[0])
        index2 = video_list.index(to_combine_list[1])
        if abs(index1-index2) > 1:
            to_combine_list.pop(0)
        else:
            a = project_path+to_combine_list[0]
            b = project_path+to_combine_list[1]
            #regex
            reg = video_target_name+"(.+)\."
            num1 = re.search(reg, a).group(1)
            num2 = re.search(reg, b).group(1)
            target = video_path+video_target_name+str(num1)+"-"+str(num2)+video_target_format

            arg = '[0:v:0] [1:v:0] concat=n=2:v=1 [v]'
            cmd = ["ffmpeg","-i",a,"-i",b,"-filter_complex",arg,"-map","[v]","-y",project_path+target]
            subprocess_call(cmd)
            video_list.pop(index2)
            video_list.pop(index1)
            video_list.insert(index1, target)
            to_combine_list.pop(0)
            to_combine_list.pop(0)
            to_combine_list.insert(0, target)

            #updating scene_list
            scene_list.pop(index2)
            update_scenes(scene_list, fps, read)

    return video_list

def cut(scene_list, video_list, vid, time, fps, read):
    src = video_list[vid]
    # regex time
    sec = float(re.search('[0-9]+\.([0-9]{1})', str(time)).group(0))

    #choosing best frame to cut
    cut_time = statfile_cut(scene_list, vid, sec, fps, read)

    #calulating absolute frame for updating scene list
    frame_in_shot = seconds_to_frame(cut_time, fps)
    frame_offset = scene_list[vid]
    frame = frame_offset+frame_in_shot

    #regex name
    reg = video_target_name+"(.+)\."
    name = re.search(reg, src).group(1)

    target1 = video_path+video_target_name+name+"(1)"+video_target_format
    target2 = video_path+video_target_name+name+"(2)"+video_target_format
    cmd = ["ffmpeg", "-i", project_path + src, "-c:av", "copy", "-ss", str(cut_time),"-y", project_path + target2]
    subprocess_call(cmd)
    cmd = ["ffmpeg","-i",project_path+src,"-c:av","copy","-ss","0.0","-t",str(cut_time),"-y",project_path+target1]
    subprocess_call(cmd)

    video_list.pop(vid)
    video_list.insert(vid, target2)
    video_list.insert(vid, target1)

    #udating scene_list
    scene_list.insert(vid+1, frame)
    update_scenes(scene_list, fps, read)
    
    return video_list

def update_scenes(scene_list, fps, read):
    with open(doc_path+scenes_name, 'w') as file:
        output_file(scene_list, file, fps, read)

def statfile_cut(scene_list, vid, time, fps, read):

    shot_begin = scene_list[vid]
    shot_end = read if (len(scene_list)<=vid+1) else scene_list[vid+1]
    print("shot end", shot_end)
    frame_in_shot = seconds_to_frame(time, fps)
    frame = shot_begin+frame_in_shot

    #checking for shot overflow
    offset = 0
    if abs(frame_in_shot-shot_begin) <= cut_range:
        offset = cut_range - abs(frame_in_shot-shot_begin)
    if abs(frame_in_shot-shot_end) <= cut_range:
        offset = abs(frame_in_shot-shot_end) - cut_range

    #csv maniulation
    with open(doc_path+statfile_name, 'r') as file:
        stat = csv.reader(file)
        stat = list(stat)
        hsv_list = []
        for i in range(2*cut_range):
            #getting hsv values in statfile
            hsv_list.append(float(stat[frame-cut_range+i+offset][4]))

        cut_frame = frame_in_shot+(hsv_list.index(max(hsv_list))-cut_range)
        cut_time = frames_to_second(cut_frame, fps)

        file.close()
        return cut_time

def automatic_threshold():
    pass

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

"""def convert_seconds_to_timeformat(a):
    minute, second = divmod(a, 60)
    hour, minute = divmod(minute, 60)
    return str(hour)+str(minute)+str(second)"""

"""def frames_to_timecode(frames, fps):
    frame = int(frames)
    return '{0:02d}:{1:02d}:{2:02d}.{3:02d}'.format(int(frame // (3600*fps)), int(frame // (60*fps))%60, int(frame // fps)%60 , int(frame % fps))"""
