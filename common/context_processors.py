#Embedded file name: ./login/common/context_processors.py
"""
context_processor for common(setting)
** \xe9\x99\xa4setting\xe5\xa4\x96\xe7\x9a\x84\xe5\x85\xb6\xe4\xbb\x96context_processor\xe5\x86\x85\xe5\xae\xb9\xef\xbc\x8c\xe5\x9d\x87\xe9\x87\x87\xe7\x94\xa8\xe7\xbb\x84\xe4\xbb\xb6\xe7\x9a\x84\xe6\x96\xb9\xe5\xbc\x8f(string)

Copyright \xc2\xa9 2012-2017 Tencent BlueKing. All Rights Reserved. \xe8\x93\x9d\xe9\xb2\xb8\xe6\x99\xba\xe4\xba\x91 \xe7\x89\x88\xe6\x9d\x83\xe6\x89\x80\xe6\x9c\x89
"""
import datetime
import urlparse
from django.conf import settings

def site_settings(request):
    real_static_url = urlparse.urljoin(settings.SITE_URL, '.' + settings.STATIC_URL)
    cur_domain = request.get_host()
    return {'LOGIN_URL': settings.LOGIN_URL,
     'LOGOUT_URL': settings.LOGOUT_URL,
     'STATIC_URL': real_static_url,
     'SITE_URL': settings.SITE_URL,
     'STATIC_VERSION': settings.STATIC_VERSION,
     'CUR_DOMIAN': cur_domain,
     'APP_PATH': request.get_full_path(),
     'NOW': datetime.datetime.now(),
     'JS_SUFFIX': settings.JS_SUFFIX,
     'CSS_SUFFIX': settings.CSS_SUFFIX}
