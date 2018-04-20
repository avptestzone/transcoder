from django.contrib import admin
from tmodel.models import Host,Channel
# Register your models here.

class ChannelsAdmin(admin.ModelAdmin):
	list_display=('id','name','sid','multicast_in','multicast_out','bitrate','pcr_period','status','command','ffmpeg_pid','parse_pid','astra_pid')

admin.site.register(Host)
admin.site.register(Channel,ChannelsAdmin)