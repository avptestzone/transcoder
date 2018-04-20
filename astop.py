#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,signal,sys

pid=int(sys.argv[1])
id=str(sys.argv[2])

try:
    os.kill(pid,signal.SIGTERM)
except OSError:
    pass

open("/etc/django/astra/conf-"+id+".conf",'w')
