import cv2
import csv
from interface.models import VideoFile
from interface.models import PySceneDetectArgs
from interface.forms import VideoForm
import scenedetect

def split(capture, output_filename, first_frame, last_frame, fps, size):

    video_writer = cv2.VideoWriter(output_filename, cv2.VideoWriter_fourcc('H','2','6','4'), fps, size)

    if not video_writer.isOpened():
        print('FATAL ERROR - could not open video writer')

    capture.set(cv2.CAP_PROP_POS_FRAMES, first_frame)

    number_of_frames = last_frame-first_frame+1

    while number_of_frames >= 0:
        ret, im = capture.read()
        video_writer.write(im)
        number_of_frames -=1
    """frame_number = capture.get(cv2.CAP_PROP_POS_FRAMES)
    while frame_number < last_frame:
        ret, frame = capture.read()
        video_writer.write(frame)
        frame_number = capture.get(cv2.CAP_PROP_POS_FRAMES)"""

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

    return name_list

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

def split_input_video(input_path, output_path, smgr, video_fps):

    scene_list_msec = [(1000.0 * x) / float(video_fps) for x in smgr.scene_list]
    scene_list_tc = [scenedetect.timecodes.get_string(x) for x in scene_list_msec]
    timecode_list_str = ','.join(scene_list_tc)
    """ Calls the mkvmerge command on the input video, splitting it at the
    passed timecodes, where each scene is written in sequence from 001."""
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

    return number