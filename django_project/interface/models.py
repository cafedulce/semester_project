from django.db import models
import os

# here is our video file model
# it is designed so in order to fit with PySceneDetect
class VideoFile(models.Model):

    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255, default='.')
    absolute_path = models.CharField(max_length=255, default='.')
    video = models.FileField(upload_to='video_files/')

    def __str__ (self):
        return self.name

    def video_name(self):
        return os.path.basename(self.video.name)

class PySceneDetectArgs(models.Model):

    # here is our arg model
    # it is also designed to fit with PySceneDetect
    name = models.CharField(max_length=255)
    detection_method = models.CharField(max_length=255, default='content')
    threshold = models.IntegerField(default=30, null=True)
    min_percent = models.IntegerField(default=95)
    min_scene_len = models.IntegerField(default=15)
    block_size = models.IntegerField(default=8)
    fade_bias = models.IntegerField(default=0)
    downscale_factor = models.IntegerField(default=5, null=False)
    frame_skip = models.IntegerField(default=0, null=False)
    save_images = models.BooleanField(default=False)
    quiet_mode = models.BooleanField(default=True)
    stats_file = models.FileField(null=True)
    output_file = models.FileField(null=True)
    start_time = models.IntegerField(null=True)
    end_time = models.IntegerField(null=True)
    duration = models.IntegerField(null=True)


    def __str__(self):
        return self.name

