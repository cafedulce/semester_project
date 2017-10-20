from django.db import models

# Create your models here.
class VideoFile(models.Model):

    name = models.CharField(max_length=255)
    video = models.FileField(upload_to='video_files/')

    def __str__ (self):
        return self.name

"""class PySceneDetectArgs(object):
    def __init__(self, input, type='content', threshold=None, save_im=False, mode=True, stats=None):
        self.input = input
        self.detection_method = type
        self.threshold = threshold
        self.min_percent = 95
        self.min_scene_len = 15
        self.block_size = 8
        self.fade_bias = 0
        self.downscale_factor = 1
        self.frame_skip = 2
        self.save_images = save_im
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.quiet_mode = mode
        self.stats_file = stats

scene_detectors = scenedetect.detectors.get_available()

smgr_content = scenedetect.manager.SceneManager(
    PySceneDetectArgs(input=path, type='content', threshold=30, save_im=False, mode=True), scene_detectors)

fps, read, processed = scenedetect.detect_scenes_file(path=path, scene_manager=smgr_content)"""

class PySceneDetectArgs(models.Model):

    name = models.CharField(max_length=255)
    detection_method = models.CharField(max_length=255, default='content')
    threshold = models.IntegerField(default=30)
    min_percent = models.IntegerField(default=95)
    min_scene_len = models.IntegerField(default=15)
    block_size = models.IntegerField(default=8)
    fade_bias = models.IntegerField(default=0)
    downscale_factor = models.IntegerField(default=1)
    frame_skip = models.IntegerField(default=2)
    save_images = models.BooleanField(default=False)
    quiet_mode = models.BooleanField(default=True)
    stats_file = models.BooleanField(default=False)
    start_time = models.IntegerField(null=True)
    end_time = models.IntegerField(null=True)
    duration = models.IntegerField(null=True)


    def __str__(self):
        return self.name