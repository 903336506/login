#Embedded file name: ./login/bkaccount/middlewares.py
"""
Login middleware

Copyright \xc2\xa9 2012-2017 Tencent BlueKing. All Rights Reserved. \xe8\x93\x9d\xe9\xb2\xb8\xe6\x99\xba\xe4\xba\x91 \xe7\x89\x88\xe6\x9d\x83\xe6\x89\x80\xe6\x9c\x89
"""
from django.conf import settings
from django.contrib.auth import authenticate
from bkaccount.accounts import Account

class LoginMiddleware(object):

    def process_view(self, request, view, args, kwargs):
        full_path = request.get_full_path()
        if full_path.startswith(settings.STATIC_URL) or full_path == '/robots.txt':
            return None
        if getattr(view, 'login_exempt', False):
            return None
        user = authenticate(request=request)
        if user:
            request.user = user
            return None
        account = Account()
        return account.redirect_login(request)
