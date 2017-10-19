from django.db import models

# Create your models here.
class VideoFile(models.Model):

    name = models.CharField(max_length=255)
    video = models.FileField(upload_to='video_files/')

    def __str__ (self):
        return self.name    

