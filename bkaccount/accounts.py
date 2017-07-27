#Embedded file name: ./login/bkaccount/accounts.py
"""
\xe8\xb4\xa6\xe5\x8f\xb7\xe4\xbd\x93\xe7\xb3\xbb\xe7\x9b\xb8\xe5\x85\xb3\xe7\x9a\x84\xe5\x9f\xba\xe7\xb1\xbbAccount

Copyright \xc2\xa9 2012-2017 Tencent BlueKing. All Rights Reserved. \xe8\x93\x9d\xe9\xb2\xb8\xe6\x99\xba\xe4\xba\x91 \xe7\x89\x88\xe6\x9d\x83\xe6\x89\x80\xe6\x9c\x89
"""
import json
import time
import unicodedata
import ldap
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import redirect_to_login
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.utils.six.moves.urllib.parse import urlparse
from common.log import logger
from bkaccount.encryption import encrypt, decrypt, salt
from bkaccount.models import Loignlog, BkToken,BkUser
from bkaccount.constants import USERNAME_CHECK_PATTERN, PASSWORD_CHECK_PATTERN


class AccountSingleton(object):
    """
    \xe5\x8d\x95\xe4\xbe\x8b\xe5\x9f\xba\xe7\xb1\xbb
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance


class Account(AccountSingleton):
    """
    \xe8\xb4\xa6\xe5\x8f\xb7\xe4\xbd\x93\xe7\xb3\xbb\xe7\x9b\xb8\xe5\x85\xb3\xe7\x9a\x84\xe5\x9f\xba\xe7\xb1\xbbAccount
    
    \xe6\x8f\x90\xe4\xbe\x9b\xe9\x80\x9a\xe7\x94\xa8\xe7\x9a\x84\xe8\xb4\xa6\xe5\x8f\xb7\xe5\x8a\x9f\xe8\x83\xbd
    """
    BK_COOKIE_NAME = settings.BK_COOKIE_NAME
    BK_COOKIE_AGE = settings.BK_COOKIE_AGE
    REDIRECT_FIELD_NAME = 'c_url'
    BK_LOGIN_URl = str(settings.LOGIN_URL)

    def is_safe_url(self, url, host = None):
        """
        \xe5\x88\xa4\xe6\x96\xadurl\xe6\x98\xaf\xe5\x90\xa6\xe4\xb8\x8e\xe5\xbd\x93\xe5\x89\x8dhost\xe7\x9a\x84\xe6\xa0\xb9\xe5\x9f\x9f\xe4\xb8\x80\xe8\x87\xb4
        
        \xe4\xbb\xa5\xe4\xb8\x8b\xe6\x83\x85\xe5\x86\xb5\xe8\xbf\x94\xe5\x9b\x9eFalse\xef\xbc\x9a
            1)\xe6\xa0\xb9\xe5\x9f\x9f\xe4\xb8\x8d\xe4\xb8\x80\xe8\x87\xb4
            2)url\xe7\x9a\x84scheme\xe4\xb8\x8d\xe4\xb8\xba\xef\xbc\x9ahttps(s)
            3)url\xe4\xb8\xba\xe7\xa9\xba
        """
        if url is not None:
            url = url.strip()
        if not url:
            return False
        url = url.replace('\\', '/')
        if url.startswith('///'):
            return False
        url_info = urlparse(url)
        if not url_info.netloc and url_info.scheme:
            return False
        if unicodedata.category(url[0])[0] == 'C':
            return False
        url_domain = url_info.netloc.split(':')[0].split('.')[-2] if url_info.netloc else ''
        host_domain = host.split(':')[0].split('.')[-2] if host else ''
        return (not url_info.netloc or url_domain == host_domain) and (not url_info.scheme or url_info.scheme in ('http', 'https'))

    def get_bk_token(self, username):
        """
        \xe7\x94\x9f\xe6\x88\x90\xe7\x94\xa8\xe6\x88\xb7\xe7\x9a\x84\xe7\x99\xbb\xe5\xbd\x95\xe6\x80\x81
        """
        bk_token = ''
        retry_count = 0
        while not bk_token and retry_count < 5:
            now_time = int(time.time())
            expire_time = now_time + self.BK_COOKIE_AGE
            plain_token = '%s|%s|%s' % (expire_time, username, salt())
            bk_token = encrypt(plain_token)
            try:
                BkToken.objects.create(token=bk_token)
            except:
                logger.exception(u'\u767b\u5f55\u7968\u636e\u4fdd\u5b58\u5931\u8d25')
                bk_token = '' if retry_count < 4 else bk_token

            retry_count += 1

        return bk_token

    def _is_bk_token_valid(self, bk_token):
        """
        \xe9\xaa\x8c\xe8\xaf\x81\xe7\x94\xa8\xe6\x88\xb7\xe7\x99\xbb\xe5\xbd\x95\xe6\x80\x81
        """
        if not bk_token:
            error_msg = u'\u7f3a\u5c11\u53c2\u6570'
            return (False, error_msg)
        try:
            plain_bk_token = decrypt(bk_token)
        except:
            plain_bk_token = ''
            logger.exception(u'\u53c2\u6570[%s]\u89e3\u6790\u5931\u8d25' % bk_token)

        if not plain_bk_token:
            error_msg = u'\u53c2\u6570\u975e\u6cd5'
            return (False, error_msg)
        token_info = plain_bk_token.split('|')
        if not token_info or len(token_info) < 3:
            error_msg = u'\u53c2\u6570\u975e\u6cd5'
            return (False, error_msg)
        try:
            is_logout = BkToken.objects.get(token=bk_token).is_logout
        except:
            error_msg = u'\u53c2\u6570\u975e\u6cd5'
            return (False, error_msg)

        expire_time = int(token_info[0])
        now_time = int(time.time())
        if is_logout or now_time > expire_time or expire_time - now_time > self.BK_COOKIE_AGE:
            error_msg = u'\u767b\u5f55\u6001\u5df2\u8fc7\u671f'
            return (False, error_msg)
        username = token_info[1]
        return (True, username)

    def is_bk_token_valid(self, request):
        bk_token = request.COOKIES.get(self.BK_COOKIE_NAME, None)
        return self._is_bk_token_valid(bk_token)

    def record_login_log(self, request, user, app_id):
        """
        \xe8\xae\xb0\xe5\xbd\x95\xe7\x94\xa8\xe6\x88\xb7\xe7\x99\xbb\xe5\xbd\x95\xe6\x97\xa5\xe5\xbf\x97
        """
        host = request.get_host()
        login_browser = request.META.get('HTTP_USER_AGENT', 'unknown')
        login_ip = request.META.get('HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR')
        Loignlog.objects.record_login(user, login_browser, login_ip, host, app_id)

    def redirect_login(self, request):
        """
        \xe9\x87\x8d\xe5\xae\x9a\xe5\x90\x91\xe5\x88\xb0\xe7\x99\xbb\xe5\xbd\x95\xe9\xa1\xb5\xe9\x9d\xa2.
        
        \xe7\x99\xbb\xe5\xbd\x95\xe6\x80\x81\xe9\xaa\x8c\xe8\xaf\x81\xe4\xb8\x8d\xe9\x80\x9a\xe8\xbf\x87\xe6\x97\xb6\xe8\xb0\x83\xe7\x94\xa8
        """
        if request.is_ajax():
            return HttpResponse(status=401)
        path = request.build_absolute_uri()
        resolved_login_url = resolve_url(self.BK_LOGIN_URl)
        login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
        current_scheme, current_netloc = urlparse(path)[:2]
        if (not login_scheme or login_scheme == current_scheme) and (not login_netloc or login_netloc == current_netloc):
            path = settings.SITE_URL[:-1] + request.get_full_path()
        return redirect_to_login(path, resolved_login_url, self.REDIRECT_FIELD_NAME)

    def login(self, request, template_name = 'account/login.html', authentication_form = AuthenticationForm, current_app = None, extra_context = None):
        """
        \xe7\x99\xbb\xe5\xbd\x95\xe9\xa1\xb5\xe9\x9d\xa2\xe5\x92\x8c\xe7\x99\xbb\xe5\xbd\x95\xe5\x8a\xa8\xe4\xbd\x9c
        """
        redirect_field_name = self.REDIRECT_FIELD_NAME
        redirect_to = request.POST.get(redirect_field_name, request.GET.get(redirect_field_name, ''))
        app_id = request.POST.get('app_id', request.GET.get('app_id', ''))
        if request.method == 'POST':
            user_name = request.POST.get('username')
            pwd = request.POST.get('password')
            form = authentication_form(request, data=request.POST)
            if user_name.lower() == 'admin':
                pass_login = form.is_valid()
            else:
                pass_login = self.valiedate_user(user_name,pwd)
            if pass_login:
                if not self.is_safe_url(url=redirect_to, host=request.get_host()):
                    redirect_to = resolve_url('%saccounts/' % settings.SITE_URL)
                bk_user,is_create = BkUser.objects.get_or_create(username=user_name)
                if is_create:
                    bk_user.chname = user_name
                    bk_user.save()
                #auth_login(request, form.get_user())
                #username = form.cleaned_data.get('username', '')
                username = user_name
                self.record_login_log(request, form.get_user(), app_id)
                bk_token = self.get_bk_token(username)
                response = HttpResponseRedirect(redirect_to)
                response.set_cookie(self.BK_COOKIE_NAME, bk_token, domain=settings.BK_COOKIE_DOMAIN)
                return response
        else:
            form = authentication_form(request)
        current_site = get_current_site(request)
        context = {'form': form,
         redirect_field_name: redirect_to,
         'site': current_site,
         'site_name': current_site.name,
         'app_id': app_id}
        if extra_context is not None:
            context.update(extra_context)
        if current_app is not None:
            request.current_app = current_app
        bk_token = request.COOKIES.get(self.BK_COOKIE_NAME, None)
        if bk_token:
            BkToken.objects.filter(token=bk_token).update(is_logout=True)
        response = TemplateResponse(request, template_name, context)
        response.delete_cookie(self.BK_COOKIE_NAME, domain=settings.BK_COOKIE_DOMAIN)
        return response

    def logout(self, request, next_page = None):
        """
        \xe7\x99\xbb\xe5\x87\xba\xe5\xb9\xb6\xe9\x87\x8d\xe5\xae\x9a\xe5\x90\x91\xe5\x88\xb0\xe7\x99\xbb\xe5\xbd\x95\xe9\xa1\xb5\xe9\x9d\xa2
        """
        redirect_field_name = self.REDIRECT_FIELD_NAME
        auth_logout(request)
        if redirect_field_name in request.POST or redirect_field_name in request.GET:
            next_page = request.POST.get(redirect_field_name, request.GET.get(redirect_field_name))
            if not self.is_safe_url(url=next_page, host=request.get_host()):
                next_page = request.path
        if next_page:
            response = HttpResponseRedirect(next_page)
        else:
            response = HttpResponseRedirect(self.BK_LOGIN_URl)
        bk_token = request.COOKIES.get(self.BK_COOKIE_NAME, None)
        if bk_token:
            BkToken.objects.filter(token=bk_token).update(is_logout=True)
        response.delete_cookie(self.BK_COOKIE_NAME, domain=settings.BK_COOKIE_DOMAIN)
        return response

    def _is_request_from_esb(self, request):
        """
        \xe8\xaf\xb7\xe6\xb1\x82\xe6\x98\xaf\xe5\x90\xa6\xe6\x9d\xa5\xe8\x87\xaaESB
        """
        x_app_token = request.META.get('HTTP_X_APP_TOKEN')
        x_app_code = request.META.get('HTTP_X_APP_CODE')
        if x_app_code == 'esb' and x_app_token == settings.ESB_TOKEN:
            return True
        return False

    def is_login(self, request):
        """
        \xe9\xaa\x8c\xe8\xaf\x81\xe7\x94\xa8\xe6\x88\xb7\xe7\x9a\x84\xe7\x99\xbb\xe5\xbd\x95\xe6\x80\x81
        """
        bk_token = request.GET.get(self.BK_COOKIE_NAME)
        is_valid, data = self._is_bk_token_valid(bk_token)
        if not is_valid:
            return JsonResponse({'result': False,
             'code': '1200',
             'message': data,
             'data': {}})
        return JsonResponse({'result': True,
         'code': '00',
         'message': u'\u7528\u6237\u9a8c\u8bc1\u6210\u529f',
         'data': {'username': data}})

    def get_user(self, request):
        """
        \xe8\x8e\xb7\xe5\x8f\x96\xe7\x94\xa8\xe6\x88\xb7\xe4\xbf\xa1\xe6\x81\xaf
        """
        bk_token = request.GET.get(self.BK_COOKIE_NAME)
        is_valid, token_data = self._is_bk_token_valid(bk_token)
        if not is_valid:
            _is_from_esb = self._is_request_from_esb(request)
            username = request.GET.get('username')
            if _is_from_esb and username:
                token_data = username
            else:
                return JsonResponse({'result': False,
                 'code': '1200',
                 'message': token_data,
                 'data': {}})
        user_model = get_user_model()
        try:
            user = user_model._default_manager.get_by_natural_key(token_data)
        except user_model.DoesNotExist:
            return JsonResponse({'result': False,
             'code': '1300',
             'message': u'\u7528\u6237[%s]\u4e0d\u5b58\u5728' % token_data,
             'data': {}})

        data = {'username': user.username,
         'chname': user.chname,
         'qq': user.qq,
         'phone': user.phone,
         'email': user.email,
         'role': '1' if user.is_superuser else '0'}
        return JsonResponse({'result': True,
         'code': '00',
         'message': u'\u7528\u6237\u4fe1\u606f\u83b7\u53d6\u6210\u529f',
         'data': data})

    def get_all_user(self, request):
        """
        \xe8\x8e\xb7\xe5\x8f\x96\xe6\x89\x80\xe6\x9c\x89\xe7\x94\xa8\xe6\x88\xb7\xe4\xbf\xa1\xe6\x81\xaf
        """
        _is_from_esb = self._is_request_from_esb(request)
        if not _is_from_esb:
            bk_token = request.GET.get(self.BK_COOKIE_NAME)
            is_valid, token_data = self._is_bk_token_valid(bk_token)
            if not is_valid:
                return JsonResponse({'result': False,
                 'code': '1200',
                 'message': token_data,
                 'data': {}})
        user_model = get_user_model()
        data = []
        users = user_model.objects.all()
        for user in users:
            data.append({'username': user.username,
             'chname': user.chname,
             'qq': user.qq,
             'phone': user.phone,
             'email': user.email,
             'role': '1' if user.is_superuser else '0'})

        return JsonResponse({'result': True,
         'code': '00',
         'message': u'\u7528\u6237\u4fe1\u606f\u83b7\u53d6\u6210\u529f',
         'data': data})

    def get_batch_user(self, request):
        """
        \xe6\x89\xb9\xe9\x87\x8f\xe8\x8e\xb7\xe5\x8f\x96\xe7\x94\xa8\xe6\x88\xb7\xe4\xbf\xa1\xe6\x81\xaf
        
        \xe5\x8f\x82\xe6\x95\xb0\xef\xbc\x9ausername_list:['admin', 'admin1']
        """
        try:
            post_data = json.loads(request.body)
            username_list = post_data.get('username_list')
        except:
            msg = u'\u8bf7\u6c42\u53c2\u6570\u683c\u5f0f\u9519\u8bef,\u5fc5\u987b\u4e3ajson\u683c\u5f0f'
            return JsonResponse({'result': False,
             'code': '1200',
             'message': msg,
             'data': {}})

        print '==========type:%s' % type(username_list)
        print '==========%s' % username_list
        _is_from_esb = self._is_request_from_esb(request)
        if not _is_from_esb:
            bk_token = post_data.get(self.BK_COOKIE_NAME)
            is_valid, token_data = self._is_bk_token_valid(bk_token)
            if not is_valid:
                return JsonResponse({'result': False,
                 'code': '1200',
                 'message': token_data,
                 'data': {}})
        if not username_list:
            return JsonResponse({'result': False,
             'code': '1200',
             'message': u'\u7f3a\u5c11\u53c2\u6570:username_list',
             'data': {}})
        user_model = get_user_model()
        data = {}
        users = user_model.objects.filter(username__in=username_list)
        for user in users:
            data[user.username] = {'username': user.username,
             'chname': user.chname,
             'qq': user.qq,
             'phone': user.phone,
             'email': user.email,
             'role': '1' if user.is_superuser else '0'}

        return JsonResponse({'result': True,
         'code': '00',
         'message': u'\u7528\u6237\u4fe1\u606f\u83b7\u53d6\u6210\u529f',
         'data': data})

    def reset_password(self, request):
        """
        \xe9\x87\x8d\xe7\xbd\xae\xe5\xaf\x86\xe7\xa0\x81
        """
        try:
            post_data = json.loads(request.body)
        except:
            msg = u'\u8bf7\u6c42\u53c2\u6570\u683c\u5f0f\u9519\u8bef,\u5fc5\u987b\u4e3ajson\u683c\u5f0f'
            return JsonResponse({'result': False,
             'code': '1200',
             'message': msg,
             'data': {}})

        bk_token = post_data.get(self.BK_COOKIE_NAME)
        is_valid, token_data = self._is_bk_token_valid(bk_token)
        if not is_valid:
            return JsonResponse({'result': False,
             'code': '1200',
             'message': token_data,
             'data': {}})
        username = post_data.get('username')
        new_password = post_data.get('new_password', '').strip()
        if not PASSWORD_CHECK_PATTERN.match(new_password):
            msg = u'\u5bc6\u7801\u4ec5\u5305\u542b\u6570\u5b57\u3001\u5b57\u6bcd\u6216!@#$%^*()_-+=\uff0c\u957f\u5ea6\u57284-20\u4e2a\u5b57\u7b26'
            return JsonResponse({'result': False,
             'code': '1200',
             'message': msg,
             'data': {}})
        user_model = get_user_model()
        try:
            user = user_model.objects.get(username=username)
        except:
            msg = u'\u7528\u6237\u540d[%s]\u4e0d\u5b58\u5728' % username
            return JsonResponse({'result': False,
             'code': '1201',
             'message': msg,
             'data': {}})

        try:
            user.set_password(new_password)
            user.save()
        except:
            msg = u'\u7528\u6237[%s]\u5bc6\u7801\u91cd\u7f6e\u5931\u8d25' % username
            logger.exception(msg)
            return JsonResponse({'result': False,
             'code': '1202',
             'message': msg,
             'data': {}})

        return JsonResponse({'result': True,
         'code': '00',
         'message': u'\u5bc6\u7801\u91cd\u7f6e\u6210\u529f',
         'data': {}})

    def modify_user_info(self, request):
        """
        \xe4\xbf\xae\xe6\x94\xb9\xe7\x94\xa8\xe6\x88\xb7\xe5\x9f\xba\xe6\x9c\xac\xe4\xbf\xa1\xe6\x81\xaf
        """
        try:
            post_data = json.loads(request.body)
        except:
            msg = u'\u8bf7\u6c42\u53c2\u6570\u683c\u5f0f\u9519\u8bef,\u5fc5\u987b\u4e3ajson\u683c\u5f0f'
            return JsonResponse({'result': False,
             'code': '1200',
             'message': msg,
             'data': {}})

        bk_token = post_data.get(self.BK_COOKIE_NAME)
        is_valid, token_data = self._is_bk_token_valid(bk_token)
        if not is_valid:
            return JsonResponse({'result': False,
             'code': '1200',
             'message': token_data,
             'data': {}})
        username = post_data.get('username')
        if not USERNAME_CHECK_PATTERN.match(username):
            msg = u'\u7528\u6237\u540d\u3010%s\u3011\u9519\u8bef\uff0c\u5fc5\u987b\u5305\u542b\u6570\u5b57\u548c\u5b57\u6bcd\uff0c\u957f\u5ea6\u57284-20\u4e2a\u5b57\u7b26' % username
            return JsonResponse({'result': False,
             'code': '1200',
             'message': token_data,
             'data': {}})
        user_model = get_user_model()
        try:
            user = user_model.objects.get(username=username)
        except:
            msg = u'\u7528\u6237\u540d[%s]\u4e0d\u5b58\u5728' % username
            return JsonResponse({'result': False,
             'code': '1201',
             'message': msg,
             'data': {}})

        chname = post_data.get('chname').strip()
        qq = post_data.get('qq').strip()
        phone = post_data.get('phone').strip()
        email = post_data.get('email').strip()
        try:
            user.chname = chname
            user.qq = qq
            user.phone = phone
            user.email = email
            user.save()
        except:
            msg = u'\u4e2a\u4eba[%s]\u4fe1\u606f\u4fee\u6539\u5931\u8d25' % username
            logger.exception(msg)
            JsonResponse({'result': False,
             'code': '1202',
             'message': msg,
             'data': {}})

        return JsonResponse({'result': True,
         'code': '00',
         'message': u'\u7528\u6237\u4fe1\u606f\u4fee\u6539\u6210\u529f',
         'data': {}})
    def valiedate_user(self,username,password):
        LDAP_PROVIDER_BASE = 'ou=Yunwei,ou=ZHUYUN,dc=jiagouyun,dc=com'  # 不允许有空格
        LDAP_PROVIDER_URL = 'ldap://118.178.56.52:389/'  # 测试
        username = username +',' +LDAP_PROVIDER_BASE
        try:
            ldapServer = ldap.initialize(LDAP_PROVIDER_URL)
            ldapServer.protocol_version = ldap.VERSION3
            ldapServer.bind_s(username, password)
            ldapServer.unbind_s()
            return True
        except ldap.INVALID_CREDENTIALS:
            return False