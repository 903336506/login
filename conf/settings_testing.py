#!/usr/bin/env python
# encoding: utf-8
"""
测试环境配置
"""

DEBUG = True

# use the static root 'static' in production envs
if not DEBUG:
    STATIC_ROOT = 'static'

# 数据库配置信息
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',   # 默认用mysql
        'NAME': 'open_paas',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

# 初始化用户名、密码
USERNAME = 'admin'
PASSWORD = 'admin'

# cookie访问域
BK_COOKIE_DOMAIN = '.bking.com'

SECRET_KEY = 'jO149njrTj4kEx6ZbUH8Zc53bfQJctINWaEzTWIsOoxSDNwK2I'

# ESB Token
ESB_TOKEN = '41f076b7-afce-46eb-9e85-dab245eb0931'
