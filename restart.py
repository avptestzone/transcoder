#!/usr/bin/python
# -*- coding: utf-8 -*-

import re,os,time,signal,datetime,django
from subprocess import Popen, PIPE
 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "transcoder.settings")
django.setup()

from tmodel.models import Channel

def start_channel (channel):
    
    cid=str(channel.id)
    log=open('/etc/django/logs/' + cid +'.log','w')
    temp=open('/etc/django/stdout/' + cid +'-stdout.log','w+')

    temp.truncate() 

    command='ffmpeg -hide_banner -re -i http://127.0.0.1:8000/udp/{0}#pnr={1} '.format(channel.multicast_in,channel.sid) 
    command += channel.command.replace('|','\\|')
    command += ' -map 0:p:{1}:0 -map 0:p:{1}:1 -mpegts_service_id {1} -mpegts_pmt_start_pid 2048 -metadata service_provider=\'Ufanet\' -metadata service_name={0} -muxrate {2}M -threads 4 -flush_packets 0 -pcr_period {3} -pat_period 0.1 -tables_version 31 -f mpegts udp://127.0.0.1:{5}?pkt_size=1316\&buffer_size=65535'.format(channel.name,channel.sid,channel.bitrate,channel.pcr_period,channel.multicast_out,str(int(cid)+1000))
    command += ' 2>> /etc/django/stdout/' + cid +'-stdout.log' 
  
    ffmpeg_pid=Popen(command, shell=True).pid
    Channel.objects.filter(id=cid).update(ffmpeg_pid=ffmpeg_pid+1)
    time.sleep(1)
    

    start_time=datetime.datetime.now() + datetime.timedelta(hours=5)
    log.write(start_time.strftime("[%d.%m.%Y %H:%M:%S]") + ' Channel start\r\n\r\n')

    check=1
    while check:
        time.sleep(1)
        output=temp.read()
        log.write(output)
            
        if re.findall(r'frame=\s*',output):
            temp.seek(0)
            temp.truncate()           
            ffmpeg_start=True
            check=0
        else:
            check+=1

            if check>15:
                check=0
                ffmpeg_start=False
    
    temp.close()
    log.close()         


    if ffmpeg_start:
        Channel.objects.filter(id=cid).update(status=1)
        
        make_astra_config(cid,channel.name,channel.multicast_out,channel.bitrate)
        astra_pid=Popen("sudo /opt/bin/astra /etc/django/astra/conf-"+cid+".conf --no-stdout --log /etc/django/astra/log-"+cid+".log", shell=True).pid
        Channel.objects.filter(id=cid).update(astra_pid=astra_pid+1) 

        parse_pid=Popen("/etc/django/transcoder/parser.py "+cid+" &", shell=True).pid
        Channel.objects.filter(id=cid).update(parse_pid=parse_pid+1)
        
    else:
        Channel.objects.filter(id=cid).update(status=3)
        os.kill(ffmpeg_pid,signal.SIGTERM)
        os.kill(ffmpeg_pid-1,signal.SIGTERM)

    
    time.sleep(1)


def make_astra_config(ind,nam,m_out,bit):
    
    config='make_channel ({{ name = "{1}", input = {{ "udp://127.0.0.1:{0}"}}, output = {{"udp://{2}#sync&cbr={3}"}}}})'.format(str(int(ind)+1000),nam,m_out,bit)

    with open('/etc/django/astra/conf-' + ind +'.conf','w') as astra:
        astra.write(config)


Channel.objects.filter(status=1).update(status=0)
channel_list=Channel.objects.all()

for ch in channel_list:
    start_channel(ch)        
  
