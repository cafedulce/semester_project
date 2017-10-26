import cv2

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

    return 1

def splitter(filename, scene_list, project_path, output_prefix):

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

    begin_frame = 0
    for frame in scene_list:
        name = output_prefix+str(begin_frame)+'.mp4'
        name_list.append(name)
        split(capture, project_path+name, begin_frame, frame, fps, size)
        begin_frame = frame

    return name_list