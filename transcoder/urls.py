"""transcoder URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from . import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index),
    url(r'^channels/$', views.base),
    url(r'^add_channel/$', views.add_channel),
    url(r'^delete_channel_ask/$', views.send_confirm),
    url(r'^delete_channel/(\d+)$', views.delete_channel),
    url(r'^show_channel/(\d+)$', views.show_channel),
    url(r'^show_log/(\d+)$', views.show_full_log),
    url(r'^edit_channel_data/(\d+?)/(.+?)/(.+?)$', views.edit_channel_data),
    url(r'^run_channel_phase1/(\d+)$', views.run_channel_phase1),
    url(r'^run_channel_phase2/(\d+)$', views.run_channel_phase2),
    url(r'^run_channel_phase3/(\d+)$', views.run_channel_phase3),
    url(r'^stop_channel_phase1/(\d+)$', views.stop_channel_phase1),
    url(r'^stop_channel_phase2/(\d+)$', views.stop_channel_phase2),
    url(r'^stop_channel_phase3/(\d+)$', views.stop_channel_phase3),
]