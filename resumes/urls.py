# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# ======================================================================
#   Copyright (C) 2022 liaozhimingandy@qq.com Ltd. All Rights Reserved.
#
#   @Author      : zhiming
#   @Project     : proj_django_resume
#   @File Name   : urls.py
#   @Created Date: 2022-06-23 22:47
#      @Software : PyCharm
#         @e-Mail: liaozhimingandy@qq.com
#   @Description : app内部url
#
# ======================================================================
from django.urls import re_path

from .views import show, test_async

app_name = 'resumes'

urlpatterns = [
    re_path(r'^test_async/$', test_async, name="test_async"),
    re_path(r'^(?P<username>\w+)/$', show, name='show-resumes'),
    # re_path('^$', IndexView.as_view(), name='index'),
    # path('basicinfo/<int:pk>/update', BasicInfoUpdate.as_view(), name='basicinfo-update'),
    # re_path(r'^(?:detail/(?:(?P<model>\w+)/(?P<pk>\d+)))/$', DetailModelView.as_view(), name='detail'),
    # re_path(r'^(?:list/(?P<model>\w+))/$', ListModelView.as_view(), name='list'),
    # re_path(r'^(?:update/(?P<model>\w+)/(?P<pk>\d+))/$', UpdateModelView.as_view(), name='update'),
    # re_path(r'^(?:new/(?P<model>\w+))/$', NewModelView.as_view(), name='new'),
]
