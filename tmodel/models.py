from __future__ import unicode_literals
from django.db import models

# Create your models here.

class Host(models.Model):
	cpu_load=models.FloatField()
	load_average=models.CharField(max_length=30)
	em2_load=models.FloatField()
	em3_load=models.FloatField()

class Channel(models.Model):
    name=models.CharField(max_length=40)
    multicast_in=models.CharField(max_length=25)
    multicast_out=models.CharField(max_length=25)	
    command=models.TextField()
    status=models.IntegerField()
    sid = models.IntegerField()
    bitrate = models.IntegerField()
    pcr_period = models.IntegerField()
    ffmpeg_pid = models.IntegerField()
    parse_pid = models.IntegerField()
    astra_pid = models.IntegerField()

 
    def __unicode__(self):
        return self.name