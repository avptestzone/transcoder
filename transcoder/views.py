# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.contrib import auth
from subprocess import Popen, PIPE
from tmodel.models import Channel
from forms import ChannelForm,AuthForm
from collections import deque

import re,os,time,signal,datetime,sys,telnetlib


@csrf_protect
def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/channels')

    if request.method == 'POST':
        form=AuthForm(request.POST)

        if not form.is_valid():
            return render(request, "auth.html", {'form':form})

        user=auth.authenticate(username=request.POST.get('login',''), password=request.POST.get('password','')) 
            
        if user and user.is_active:
            auth.login(request, user)
            return HttpResponseRedirect('/channels')
        else:
            error='Не верное имя пользователя или пароль'
            return render(request, "auth.html", {'form':form,'deny_auth':error})

    return render(request, "auth.html")                   



def base(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    cmd=Popen("uptime", shell=True, stdin=PIPE, stdout=PIPE).stdout.read()
    load=re.findall(r'load average: (.*)',cmd)   

    channel_list=Channel.objects.filter(status=1)

    for chnl in channel_list:

        if not os.path.exists('/proc/' + str(chnl.parse_pid)):
            Channel.objects.filter(id=chnl.id).update(status=3)

            try:
                os.kill(chnl.ffmpeg_pid,signal.SIGTERM)
            except OSError:
                pass

            Popen("sudo /etc/django/transcoder/astop.py "+ str(chnl.astra_pid) +" "+str(chnl.id), shell=True)        

        if not os.path.exists('/proc/' + str(chnl.ffmpeg_pid)):
            Channel.objects.filter(id=chnl.id).update(status=3)
            
            try:
                os.kill(chnl.parse_pid,signal.SIGTERM)
            except OSError:
                pass

            Popen("sudo /etc/django/transcoder/astop.py "+ str(chnl.astra_pid) +" "+str(chnl.id), shell=True)

        if not os.path.exists('/proc/' + str(chnl.astra_pid)):
            Channel.objects.filter(id=chnl.id).update(status=3)

            try:
                os.kill(chnl.parse_pid,signal.SIGTERM)
            except OSError:
                pass

            try:
                os.kill(chnl.ffmpeg_pid,signal.SIGTERM)
            except OSError:
                pass    


    channel_list=Channel.objects.all() 

    return render(request,'channels.html',{'channels':channel_list, 'load':load[0]})


def add_channel(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        form=ChannelForm(request.POST)

        if not form.is_valid():  
            return render(request,'add_channel_form.html',{'form':form})
        
        ch_data=form.cleaned_data

        if ch_data['multicast_in'] == ch_data['multicast_out']:    
            return render(request,'add_channel_form.html',{'form':form, 'm_error':True})
        else:
            new_channel=Channel(name=ch_data['name'],
                                sid=ch_data['sid'],
                                multicast_in=ch_data['multicast_in'],
                                multicast_out=ch_data['multicast_out'],
                                bitrate=ch_data['bitrate'],
                                pcr_period=ch_data['pcr_period'],
                                command=ch_data['command'],
                                status=False,
                                ffmpeg_pid=1,
                                parse_pid=1,
                                astra_pid=1,)
            new_channel.save()
            
            return HttpResponseRedirect('/channels')                        
    return render(request,'add_channel_form.html')        


def send_confirm (request):
    return render(request,'confirm_delete.html')


def delete_channel(request, id):
    if not request.user.is_authenticated():
        return render(request,'delete_response.html',{'result':'negative'})
    else:
        Channel.objects.filter(id=id).delete()
        return render(request,'delete_response.html',{'result':'positive'}) 



def show_channel (request, id):
    ch_info=Channel.objects.filter(id=id) 
    return render(request,'channel_info.html',{'ch_info':ch_info,'log':return_short_log(id),'params':read_params(id)})


def edit_channel_data (request, id, name, data):
    d={name:data}
    form=ChannelForm(d)

    if form[name].errors:
        return render(request,'info_response.html',{'error':form[name].errors}) 
    else:
        Channel.objects.filter(id=id).update(**d)
        return render(request,'info_response.html') 

       
def run_channel_phase1 (request, id):
    Channel.objects.filter(id=id).update(status=2)
    return render(request,'return_progress_bar.html')    


def run_channel_phase2 (request, id):
    channel=Channel.objects.get(id=id)

    log=open('/etc/django/logs/' + id +'.log','w')
    temp=open('/etc/django/stdout/' + id +'-stdout.log','w+')

    temp.truncate() 

    command='ffmpeg -hide_banner -i http://127.0.0.1:8000/udp/{0}#pnr={1} '.format(channel.multicast_in,channel.sid) #+  +  
    command += channel.command.replace('|','\\|')
    command += ' -map 0:p:{1}:0 -map 0:p:{1}:1 -mpegts_service_id {1} -mpegts_pmt_start_pid 2048 -metadata service_provider=\'Ufanet\' -metadata service_name={0} -muxrate {2}M -threads 4 -flush_packets 0 -pcr_period {3} -tables_version 31 -f mpegts udp://127.0.0.1:{5}?pkt_size=1316\&buffer_size=65535'.format(channel.name,channel.sid,channel.bitrate,channel.pcr_period,channel.multicast_out,str(int(id)+1000))
    command += ' 2>> /etc/django/stdout/' + id +'-stdout.log' 
  
    ffmpeg_pid=Popen(command, shell=True).pid
    Channel.objects.filter(id=id).update(ffmpeg_pid=ffmpeg_pid+1)
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
        Channel.objects.filter(id=id).update(status=1)
        
        make_astra_config(id,channel.name,channel.multicast_out,channel.bitrate)
        astra_pid=Popen("sudo /opt/bin/astra /etc/django/astra/conf-"+id+".conf --no-stdout --log /etc/django/astra/log-"+id+".log", shell=True).pid
        Channel.objects.filter(id=id).update(astra_pid=astra_pid+1) 

        parse_pid=Popen("/etc/django/transcoder/parser.py "+id+" &", shell=True).pid
        Channel.objects.filter(id=id).update(parse_pid=parse_pid+1)
        
    else:
        Channel.objects.filter(id=id).update(status=3)
        os.kill(ffmpeg_pid,signal.SIGTERM)
        os.kill(ffmpeg_pid-1,signal.SIGTERM)

    
    time.sleep(1)
    return render(request,'return_status.html', {'status':ffmpeg_start})


def run_channel_phase3 (request, id):
    return render(request,'return_short_log.html',{'log':return_short_log(id)})


def stop_channel_phase1 (request, id):
    Channel.objects.filter(id=id).update(status=2)
    return render(request,'return_progress_bar.html')


def stop_channel_phase2 (request, id):
    channel=Channel.objects.get(id=id)
    stop='error'
     
    try:
        os.kill(channel.ffmpeg_pid,signal.SIGTERM)
    except OSError:
        pass

    try:
        os.kill(channel.parse_pid,signal.SIGTERM)
    except OSError:
        pass

    Popen("sudo /etc/django/transcoder/astop.py "+ str(channel.astra_pid) +" "+id, shell=True)

    time.sleep(1)
    
    with open('/etc/django/stdout/' + id +'-stdout.log','r+') as tailstdout:
        with open('/etc/django/logs/' + id +'.log','a') as taillog:

            end_time=datetime.datetime.now() + datetime.timedelta(hours=5)
            taillog.write(end_time.strftime("[%d.%m.%Y %H:%M:%S]") + ' Channel stop\r\n\r\n')

            for line in tailstdout:  
                taillog.write(line)

        tailstdout.seek(0)
        tailstdout.truncate()
        stop='done'
 
    tailstdout.close()
    taillog.close()

    return render(request,'return_status.html',{'status':stop})


def stop_channel_phase3 (request, id):
    Channel.objects.filter(id=id).update(status=0)
    return render(request,'return_short_log.html',{'log':return_short_log(id)}) 



def return_short_log (id):  
    log_text=''
    
    if os.path.exists('/etc/django/logs/' + id +'.log'):
        with open('/etc/django/logs/' + id +'.log','r') as log:
            for line in deque(log, 30):
                log_text+=line
            log_text = unicode(log_text, errors='ignore')
    else:
        log=open('/etc/django/logs/' + id +'.log','w')
        log.close()

    return log_text        



def show_full_log (request, id):
    log_text=[]
    
    if os.path.exists('/etc/django/logs/' + id +'.log'):
        with open('/etc/django/logs/' + id +'.log','r') as log:
            for line in log:
                string = unicode(line, errors='ignore')
                log_text.append(string)          

    return render(request,'return_log.html',{'log':log_text,'type':'2'})


def read_params (id):
    params=''

    if os.path.exists('/etc/django/data/' + id +'.log'):
        with open('/etc/django/data/' + id +'.log','r') as data:
            params=data.read()

    return params

def make_astra_config(ind,nam,m_out,bit):
    
    config='make_channel ({{ name = "{1}", input = {{ "udp://127.0.0.1:{0}"}}, output = {{"udp://{2}#sync&cbr={3}"}}}})'.format(str(int(ind)+1000),nam,m_out,bit)

    with open('/etc/django/astra/conf-' + ind +'.conf','w') as astra:
        astra.write(config)
