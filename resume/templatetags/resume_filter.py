# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# ======================================================================
#   Copyright (C) 2022 liaozhimingandy@qq.com Ltd. All Rights Reserved.
#
#   @Author      : zhiming
#   @Project     : proj_django_resume
#   @File Name   : resume_filter.py
#   @Created Date: 2022-06-25 22:21
#      @Software : PyCharm
#         @e-Mail: liaozhimingandy@qq.com
#   @Description : 自定义djaong模板过滤器
#
# ======================================================================
from django import template
register = template.Library()


@register.filter(name='value_split')
def value_split(value, separator=','):
    return value.split(separator)



