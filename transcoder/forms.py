# -*- coding: utf-8 -*-
from django import forms
from tmodel.models import Channel
import re

class ChannelForm(forms.Form):
    name = forms.CharField(max_length=20)
    multicast_in = forms.RegexField(regex='^(25[0-5]|2[0-4][0-9]|[0-1][0-9]{2}|[0-9]{2}|[0-9])(\.(25[0-5]|2[0-4][0-9]|[0-1][0-9]{2}|[0-9]{2}|[0-9])){3}:\d{4}$')
    multicast_out = forms.RegexField(regex='^(25[0-5]|2[0-4][0-9]|[0-1][0-9]{2}|[0-9]{2}|[0-9])(\.(25[0-5]|2[0-4][0-9]|[0-1][0-9]{2}|[0-9]{2}|[0-9])){3}:\d{4}$')
    command = forms.CharField(widget=forms.Textarea,max_length=1000)
    sid = forms.IntegerField()
    bitrate = forms.IntegerField(min_value=2,max_value=10)
    pcr_period = forms.IntegerField(min_value=10,max_value=100)
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if re.search(r'[^a-z0-9_]',name):
        	raise forms.ValidationError('Имя должно состоять только из строчных латинких букв, цифр и подчекивания')
        
        if Channel.objects.filter(name=name):
            raise forms.ValidationError('Данное имя уже существует')

        return name

    def clean_multicast_in(self):
        multicast_in = self.cleaned_data['multicast_in']

        if Channel.objects.filter(multicast_in=multicast_in) or Channel.objects.filter(multicast_out=multicast_in):
            raise forms.ValidationError('Данный мультикаст уже существует')

        return multicast_in

    def clean_multicast_out(self):
        multicast_out = self.cleaned_data['multicast_out']

        if Channel.objects.filter(multicast_in=multicast_out) or Channel.objects.filter(multicast_out=multicast_out):
            raise forms.ValidationError('Данный мультикаст уже существует')

        return multicast_out 

    def clean_command(self):
        command = self.cleaned_data['command']
        if re.search(r'[^a-zA-Z0-9_ \-+|=:()/\.\",]',command):
            raise forms.ValidationError('Недопустимые символы')

        return command           

class AuthForm(forms.Form):
    login = forms.CharField(max_length=20)
    password = forms.CharField(max_length=20)