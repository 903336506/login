#Embedded file name: ./login/bkaccount/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from bkaccount.accounts import Account

class BkBackend(ModelBackend):
    """
    \xe8\x87\xaa\xe5\xae\x9a\xe4\xb9\x89\xe8\xae\xa4\xe8\xaf\x81\xe6\x96\xb9\xe6\xb3\x95
    """

    def authenticate(self, request):
        account = Account()
        login_status, username = account.is_bk_token_valid(request)
        if not login_status:
            return None
        user_model = get_user_model()
        try:
            user = user_model._default_manager.get_by_natural_key(username)
            return user
        except user_model.DoesNotExist:
            return None
