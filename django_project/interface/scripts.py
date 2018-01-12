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

    #this method is used to get the values given by the user, and prepare them to be used by the detection algorithm
    video_file = VideoFile()
    video_file.video = form.cleaned_data["video"]
    video_file.name = video_file.video_name()
    video_file.path = video_path + video_file.name
    video_file.absolute_path = project_path + video_file.path
    video_file.save()

    scenedetect_object = PySceneDetectArgs()
    scenedetect_object.name = video_file.absolute_path
    scenedetect_object.detection_method = form.cleaned_data["type"]
    if form.cleaned_data["threshold"]:
        scenedetect_object.threshold = form.cleaned_data["threshold"]
    if form.cleaned_data["downscale"]:
        scenedetect_object.downscale_factor = form.cleaned_data["downscale"]

    stat = open(doc_path+statfile_name, 'w')
    scenedetect_object.stats_file = stat

    out = open(doc_path+scenes_name, 'w')
    scenedetect_object.output_file = out

    return video_file, scenedetect_object


def output_file(scene_list, file, video_fps, frames_read):

    #this function comes directly from PyScenDetect, and is a bit adjusted to fit in the webapp
    # it is used to prepare the timecodes and values to write in the csv file.

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
    #this function is also from PySceneDetect

    # Outputs the list of scenes in human-readable format to a CSV file for further analysis.

    # Output timecodes to CSV file if required (and scenes were found).

    if csv_file and len(scene_list) > 0:
        csv_writer = csv.writer(csv_file)
        # Output timecode scene list
        csv_writer.writerow(scene_list_tc)
        # Output detailed, human-readable scene list.
        csv_writer.writerow(["Scene Number", "Frame Number (Start)",
                             "Timecode", "Start Time (seconds)", "Length (seconds)"])
        for i, _ in enumerate(scene_list):
            csv_writer.writerow([str(i+1), str(scene_list[i]),scene_list_tc[i], str(scene_start_sec[i]),str(scene_len_sec[i])])


def ffmpeg_split(list, filename, fps, read):

    # function that allows the cutting of the video in different shots, that were found just after the PySceneDetect process

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

    #function that allows the combine of two or more shots in one shot

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

    #function that cut shots during the cut&combine part
    # calls the function statfile_cut to get a precise cut

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

    #function that return the precise cut time according to the statfile

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

    #implement here a way to set the threshold dinamically.

    pass
