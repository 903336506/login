#Embedded file name: ./login/bkaccount/views.py
"""
Copyright \xc2\xa9 2012-2017 Tencent BlueKing. All Rights Reserved. \xe8\x93\x9d\xe9\xb2\xb8\xe6\x99\xba\xe4\xba\x91 \xe7\x89\x88\xe6\x9d\x83\xe6\x89\x80\xe6\x9c\x89
"""
import xlrd
import xlwt
import StringIO
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseRedirect, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Q
from bkaccount.accounts import Account
from bkaccount.decorators import login_exempt
from bkaccount.models import BkUser
from bkaccount.constants import USERNAME_CHECK_PATTERN, PASSWORD_CHECK_PATTERN
from common.log import logger

@login_exempt
def login(request):
    """
    \xe7\x99\xbb\xe5\x85\xa5
    """
    account = Account()
    return account.login(request)


@login_exempt
def logout(request):
    """
    \xe7\x99\xbb\xe5\x87\xba
    """
    account = Account()
    return account.logout(request)


@login_exempt
def is_login(request):
    """
    \xe7\x99\xbb\xe5\xbd\x95\xe6\x80\x81\xe9\xaa\x8c\xe8\xaf\x81API
    """
    account = Account()
    return account.is_login(request)


@login_exempt
def get_user(request):
    """
    \xe8\x8e\xb7\xe5\x8f\x96\xe7\x94\xa8\xe6\x88\xb7\xe4\xbf\xa1\xe6\x81\xafAPI
    """
    account = Account()
    return account.get_user(request)


@login_exempt
def get_all_user(request):
    """
    \xe8\x8e\xb7\xe5\x8f\x96\xe6\x89\x80\xe6\x9c\x89\xe7\x94\xa8\xe6\x88\xb7\xe4\xbf\xa1\xe6\x81\xafAPI
    """
    account = Account()
    return account.get_all_user(request)


@csrf_exempt
@login_exempt
def get_batch_user(request):
    """
    \xe6\x89\xb9\xe9\x87\x8f\xe8\x8e\xb7\xe5\x8f\x96\xe7\x94\xa8\xe6\x88\xb7\xe4\xbf\xa1\xe6\x81\xafAPI
    """
    account = Account()
    return account.get_batch_user(request)


@csrf_exempt
@login_exempt
def reset_password(request):
    """
    \xe9\x87\x8d\xe7\xbd\xae\xe5\xaf\x86\xe7\xa0\x81
    """
    account = Account()
    return account.reset_password(request)


@csrf_exempt
@login_exempt
def modify_user_info(request):
    """
    \xe4\xbf\xae\xe6\x94\xb9\xe7\x94\xa8\xe6\x88\xb7\xe4\xb8\xaa\xe4\xba\xba\xe4\xbf\xa1\xe6\x81\xaf
    """
    account = Account()
    return account.modify_user_info(request)


def csrf_failure(request, reason = ''):
    return HttpResponseForbidden(render(request, 'csrf_failure.html'), content_type='text/html')


def users(request):
    """
    \xe7\x94\xa8\xe6\x88\xb7\xe7\xae\xa1\xe7\x90\x86\xe9\xa1\xb5\xe9\x9d\xa2
    """
    default_paasword = settings.PASSWORD
    error_msg = request.GET.get('error_msg', '')
    success_msg = request.GET.get('success_msg', '')
    context = {'default_paasword': default_paasword,
     'error_msg': error_msg,
     'success_msg': success_msg}
    return render(request, 'account/users.html', context)


def get_info(request):
    """
    \xe6\x9f\xa5\xe8\xaf\xa2\xe7\x94\xa8\xe6\x88\xb7\xe4\xbf\xa1\xe6\x81\xaf
    """
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10
    except:
        page = 1
        page_size = 10

    if request.user.is_superuser:
        all_query = BkUser.objects.all().order_by('-id')
    else:
        all_query = BkUser.objects.filter(username=request.user.username)
    search_data = request.GET.get('search_data').replace('&nbsp;', '').strip()
    search_role = request.GET.get('search_role')
    if search_role:
        all_query = all_query.filter(is_superuser=search_role)
    if search_data:
        all_query = all_query.filter(Q(username__icontains=search_data) | Q(chname__icontains=search_data))
    paginator = Paginator(all_query, page_size)
    try:
        records = paginator.page(page)
    except PageNotAnInteger:
        records = paginator.page(1)
    except EmptyPage:
        records = paginator.page(paginator.num_pages)

    adjacent_pages = 3
    start_page = max(records.number - adjacent_pages, 1)
    if start_page < adjacent_pages:
        start_page = 1
    end_page = records.number + adjacent_pages + 1
    if end_page > records.paginator.num_pages - adjacent_pages + 2:
        end_page = records.paginator.num_pages + 1
    page_numbers = [ n for n in range(start_page, end_page) ]
    show_first = 1 not in page_numbers
    show_last = records.paginator.num_pages not in page_numbers
    context = {'records': records,
     'page_numbers': page_numbers,
     'show_first': show_first,
     'show_last': show_last}
    return render(request, 'account/user_table.part', context)


@require_POST
def save_user(request):
    """
    \xe6\xb7\xbb\xe5\x8a\xa0\xe3\x80\x81\xe7\xbc\x96\xe8\xbe\x91\xe7\x94\xa8\xe6\x88\xb7\xe4\xbf\xa1\xe6\x81\xaf
    """
    user_id = request.POST.get('user_id')
    username = request.POST.get('username').strip()
    chname = request.POST.get('chname').strip()
    qq = request.POST.get('qq').strip()
    phone = request.POST.get('phone').strip()
    email = request.POST.get('email').strip()
    role = request.POST.get('role')
    is_superuser = True if role == '1' else False
    try:
        if user_id:
            _user = BkUser.objects.get(id=user_id)
            if not request.user.is_superuser and request.user != _user:
                return JsonResponse({'result': False,
                 'msg': u'\u975e\u7ba1\u7406\u5458\u7528\u6237, \u6ca1\u6709\u6743\u9650\u8fdb\u884c\u64cd\u4f5c, \u8bf7\u627e\u7ba1\u7406\u5458\u7533\u8bf7\u6743\u9650!',
                 'data': ''})
            _user.username = username
            _user.chname = chname
            _user.qq = qq
            _user.phone = phone
            _user.email = email
            _user.is_superuser = is_superuser
            _user.save()
        else:
            if not request.user.is_superuser:
                return JsonResponse({'result': False,
                 'msg': u'\u975e\u7ba1\u7406\u5458\u7528\u6237, \u6ca1\u6709\u6743\u9650\u8fdb\u884c\u64cd\u4f5c, \u8bf7\u627e\u7ba1\u7406\u5458\u7533\u8bf7\u6743\u9650!',
                 'data': ''})
            _user = BkUser.objects.create(username=username, chname=chname, qq=qq, phone=phone, email=email, is_superuser=is_superuser)
            _user.set_password(settings.PASSWORD)
            _user.save()
            user_id = _user.id
    except IntegrityError:
        return JsonResponse({'result': False,
         'msg': u'\u8d26\u53f7\u4e3a\uff1a%s \u7684\u7528\u6237\u5df2\u7ecf\u5b58\u5728' % username,
         'data': user_id})
    except:
        logger.exception(u'\u4fdd\u5b58\u7528\u6237\u4fe1\u606f(%s)\u51fa\u9519' % username)
        return JsonResponse({'result': False,
         'msg': u'\u4fdd\u5b58\u7528\u6237\u4fe1\u606f(%s)\u51fa\u9519' % username,
         'data': user_id})

    return JsonResponse({'result': True,
     'msg': u'\u4fdd\u5b58\u7528\u6237\u4fe1\u606f\u6210\u529f',
     'data': user_id})


@require_POST
def del_user(request):
    """
    \xe5\x88\xa0\xe9\x99\xa4\xe7\x94\xa8\xe6\x88\xb7
    \xe5\xbf\x85\xe9\xa1\xbb\xe4\xbf\x9d\xe7\x95\x99\xe4\xb8\x80\xe4\xb8\xaa\xe7\xae\xa1\xe7\x90\x86\xe5\x91\x98\xe7\x94\xa8\xe6\x88\xb7
    """
    if not request.user.is_superuser:
        return JsonResponse({'result': False,
         'msg': u'\u975e\u7ba1\u7406\u5458\u7528\u6237, \u6ca1\u6709\u6743\u9650\u8fdb\u884c\u64cd\u4f5c, \u8bf7\u627e\u7ba1\u7406\u5458\u7533\u8bf7\u6743\u9650!',
         'data': ''})
    user_id = request.POST.get('user_id')
    username = request.POST.get('username')
    try:
        _user = BkUser.objects.get(id=user_id)
        if _user.is_superuser:
            is_superuser_exits = BkUser.objects.exclude(id=user_id).filter(is_superuser=True).exists()
            if not is_superuser_exits:
                return JsonResponse({'result': False,
                 'msg': u'\u6700\u540e\u4e00\u4e2a\u7ba1\u7406\u5458\u7528\u6237\uff0c\u4e0d\u5141\u8bb8\u5220\u9664'})
        BkUser.objects.filter(id=user_id).delete()
    except:
        logger.exception(u'\u7528\u6237(%s)\u5220\u9664\u5931\u8d25' % username)
        return JsonResponse({'result': False,
         'msg': u'\u7528\u6237(%s)\u5220\u9664\u5931\u8d25' % username})

    return JsonResponse({'result': True,
     'msg': u'\u7528\u6237(%s)\u5220\u9664\u6210\u529f' % username})


@require_POST
def change_password(request):
    user_id = request.POST.get('user_id', '')
    new_password1 = request.POST.get('new_password1', '').strip()
    new_password2 = request.POST.get('new_password2', '').strip()
    if not all([new_password1, new_password2]):
        msg = u'\u5bc6\u7801\u4e0d\u80fd\u4e3a\u7a7a'
        return JsonResponse({'result': False,
         'msg': msg})
    if new_password1 != new_password2:
        msg = u'\u4e24\u6b21\u8f93\u5165\u7684\u65b0\u5bc6\u7801\u4e0d\u4e00\u81f4'
        return JsonResponse({'result': False,
         'msg': msg})
    if not PASSWORD_CHECK_PATTERN.match(new_password1):
        msg = u'\u5bc6\u7801\u4ec5\u5305\u542b\u6570\u5b57\u3001\u5b57\u6bcd\u6216!@#$%^*()_-+=\uff0c\u957f\u5ea6\u57284-20\u4e2a\u5b57\u7b26'
        return JsonResponse({'result': False,
         'msg': msg})
    try:
        user = BkUser.objects.get(id=user_id)
        if not request.user.is_superuser and request.user != user:
            return JsonResponse({'result': False,
             'msg': u'\u975e\u7ba1\u7406\u5458\u7528\u6237, \u6ca1\u6709\u6743\u9650\u8fdb\u884c\u64cd\u4f5c, \u8bf7\u627e\u7ba1\u7406\u5458\u7533\u8bf7\u6743\u9650!',
             'data': ''})
        user.set_password(new_password1)
        user.save()
    except Exception as e:
        logger.exception(u'\u5bc6\u7801\u91cd\u7f6e\u5931\u8d25:%s' % e)
        msg = u'\u5bc6\u7801\u91cd\u7f6e\u5931\u8d25'
        return JsonResponse({'result': False,
         'msg': msg})

    return JsonResponse({'result': True,
     'msg': ''})


@require_POST
def import_data(request):
    """
    \xe6\x89\xb9\xe9\x87\x8f\xe5\xaf\xbc\xe5\x85\xa5\xe7\x94\xa8\xe6\x88\xb7
    """
    error_msg = ''
    xls_file = request.FILES['data_files']
    xls_file_filename = xls_file.name
    try:
        file_type = xls_file_filename.split('.')[-1]
    except:
        file_type = ''
        logger.exception(u'\u6279\u91cf\u5bfc\u5165\u7528\u6237\uff0c\u89e3\u6790\u6587\u4ef6\u540d\u51fa\u9519:%s' % xls_file_filename)

    if file_type not in ('xls', 'xnnlsx'):
        error_msg = u'\u6587\u4ef6\u683c\u5f0f\u9519\u8bef\uff0c\u53ea\u652f\u6301\uff1a.xls \u548c .xlsx \u6587\u4ef6'
        return HttpResponseRedirect('%saccounts/?error_msg=%s' % (settings.SITE_URL, error_msg))
    str_file = StringIO.StringIO(xls_file.read())
    wbk = xlrd.open_workbook(file_contents=str_file.read())
    sheet = wbk.sheets()[0]
    user_list = []
    for i in range(sheet.nrows - 1, 0, -1):
        try:
            user_list.append({'username': sheet.row_values(i)[0],
             'chname': sheet.row_values(i)[1],
             'qq': sheet.row_values(i)[2],
             'phone': sheet.row_values(i)[3],
             'email': sheet.row_values(i)[4]})
        except:
            logger.exception(u'\u89e3\u6790\u7528\u6237\u5bfc\u5165\u6570\u636e\u65f6\u51fa\u9519')
            error_msg = u'\u6587\u4ef6\u89e3\u6790\u51fa\u9519\uff0c\u8bf7\u4e0b\u8f7d EXCEL\u6a21\u677f\u6587\u4ef6 \u586b\u5199\u7528\u6237\u6570\u636e'
            return HttpResponseRedirect('%saccounts/?error_msg=%s' % (settings.SITE_URL, error_msg))

    try:
        with transaction.atomic():
            for _u in user_list:
                _username = _u.get('username')
                if not USERNAME_CHECK_PATTERN.match(_username):
                    error_msg = u'\u7528\u6237\u540d\u9519\u8bef\uff0c\u5fc5\u987b\u5305\u542b\u6570\u5b57\u548c\u5b57\u6bcd\uff0c\u957f\u5ea6\u57284-20\u4e2a\u5b57\u7b26:[%s]' % _username
                    raise ValueError(error_msg)
                _user, _c = BkUser.objects.get_or_create(username=_username)
                _user.chname = _u.get('chname')
                _user.qq = _u.get('qq')
                _user.phone = _u.get('phone')
                _user.email = _u.get('email')
                if _c:
                    _user.is_superuser = False
                    _user.set_password(settings.PASSWORD)
                _user.save()

    except Exception as e:
        logger.error(e)
        error_msg = u'\u7528\u6237\u5bfc\u5165\u51fa\u73b0\u5f02\u5e38%s' % e if not error_msg else error_msg

    if error_msg:
        return HttpResponseRedirect('%saccounts/?error_msg=%s' % (settings.SITE_URL, error_msg))
    else:
        return HttpResponseRedirect('%saccounts/?success_msg=%s' % (settings.SITE_URL, u'\u7528\u6237\u5bfc\u5165\u6210\u529f'))


def export_data(request):
    """
    \xe4\xbb\xa5EXCEL\xe7\x9a\x84\xe6\x96\xb9\xe5\xbc\x8f\xe5\xaf\xbc\xe5\x87\xba\xe7\x94\xa8\xe6\x88\xb7\xe6\x95\xb0\xe6\x8d\xae
    """
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename="bk_user_export.xls'
    wbk = xlwt.Workbook(encoding='gbk')
    sheet = wbk.add_sheet('Sheet1')
    for i in range(0, 22):
        sheet.col(i).width = 5328

    fnt = xlwt.Font()
    fnt.name = 'Arial'
    fnt.colour_index = 4
    fnt.bold = True
    style = xlwt.XFStyle()
    style.font = fnt
    head_list = [u'\u7528\u6237\u540d',
     u'\u4e2d\u6587\u540d',
     u'QQ',
     u'\u8054\u7cfb\u7535\u8bdd',
     u'\u5e38\u7528\u90ae\u7bb1',
     u'\u89d2\u8272']
    for i, data in enumerate(head_list):
        sheet.write(0, i, data)

    try:
        users = BkUser.objects.all().order_by('-id').order_by('-is_superuser')
        for index, _user in enumerate(users):
            role = u'\u7ba1\u7406\u5458' if _user.is_superuser else u'\u7528\u6237'
            sheet.write(index + 1, 0, _user.username)
            sheet.write(index + 1, 1, _user.chname)
            sheet.write(index + 1, 2, _user.qq)
            sheet.write(index + 1, 3, _user.phone)
            sheet.write(index + 1, 4, _user.email)
            sheet.write(index + 1, 5, role)

    except Exception as e:
        logger.error(u'\u5bfc\u51fa\u7528\u6237\u6570\u636e\u51fa\u73b0\u9519\u8bef:%s' % e)

    wbk.save(response)
    return response
