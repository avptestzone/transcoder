#!/usr/bin/python
# -*- coding: utf-8 -*-

import re,os,time,signal,datetime,sys

while 1:
    temp=open('/etc/django/stdout/' + sys.argv[1] +'-stdout.log','r+')
    log=open('/etc/django/logs/' + sys.argv[1] +'.log','a')

    for line in temp:
        error=re.findall(r'(\[.+?@.+?\].+)',line)

        if error:
            error_time=datetime.datetime.now() + datetime.timedelta(hours=5)
            log.write(error_time.strftime("[%d.%m.%Y %H:%M:%S]") +'  '+ error[0]+'\r\n')


    temp.seek(0)
    temp_data=temp.read()

    fps_str_list=re.findall(r'fps=\s*(.+?)\s',temp_data)
    quality_str_list=re.findall(r'q=\s*(.+?)\s',temp_data)
    bitrate_str_list=re.findall(r'bitrate=\s*(.+?)kbits/s',temp_data)

    fps_num_list=[]
    quality_num_list=[]
    bitrate_num_list=[]

    for x in fps_str_list:
        fps_num_list.append(float(x))

    for y in quality_str_list: 
        quality_num_list.append(float(y))
 
    for z in bitrate_str_list:
        bitrate_num_list.append(float(z))

    if not len(fps_num_list)==0:
        fps = str(int(sum(fps_num_list)/len(fps_num_list)))
    else:
        fps='0'

    if not len(quality_num_list)==0:
        quality = str (round(sum(quality_num_list)/len(quality_num_list),1))
    else:
        quality='0'

    if not len(bitrate_num_list)==0:
        bitrate = str (round(sum(bitrate_num_list)/len(bitrate_num_list),2))
    else:
        bitrate='0'

    string='fps={0} quantizer={1} bitrate={2}'.format(fps,quality,bitrate)

    with open('/etc/django/data/' + sys.argv[1] +'.log','w') as d:
        d.write(string)

    temp.seek(0)
    temp.truncate()

    temp.close()
    log.close()

    time.sleep(10)
