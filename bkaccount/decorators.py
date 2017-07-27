#Embedded file name: ./login/bkaccount/decorators.py
from functools import wraps
from django.utils.decorators import available_attrs
from django.conf import settings
from common.log import logger

def login_exempt(view_func):
    """
    \xe7\x99\xbb\xe5\xbd\x95\xe8\xb1\x81\xe5\x85\x8d,\xe8\xa2\xab\xe6\xad\xa4\xe8\xa3\x85\xe9\xa5\xb0\xe5\x99\xa8\xe4\xbf\xae\xe9\xa5\xb0\xe7\x9a\x84action\xe5\x8f\xaf\xe4\xbb\xa5\xe4\xb8\x8d\xe6\xa0\xa1\xe9\xaa\x8c\xe7\x99\xbb\xe5\xbd\x95
    """

    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)

    wrapped_view.login_exempt = True
    return wraps(view_func, assigned=available_attrs(view_func))(wrapped_view)
