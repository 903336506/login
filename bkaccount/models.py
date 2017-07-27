#Embedded file name: ./login/bkaccount/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class BkUserManager(BaseUserManager):
    """
    BK user manager
    """

    def _create_user(self, username, password, is_superuser, **extra_fields):
        """
        Create and saves a User with the given username and password
        """
        if not username:
            raise ValueError(u'\u8bf7\u586b\u5199\u7528\u6237\u540d')
        now = timezone.now()
        user = self.model(username=username, is_superuser=is_superuser, last_login=now, date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password = None, **extra_fields):
        return self._create_user(username, password, False, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        return self._create_user(username, password, True, **extra_fields)


class BkUser(AbstractBaseUser, PermissionsMixin):
    """
    BK user
    
    username and password are required. Other fields are optional.
    """
    username = models.CharField(u'\u7528\u6237\u540d', max_length=128, unique=True)
    chname = models.CharField(u'\u4e2d\u6587\u540d', max_length=254, blank=True)
    qq = models.CharField(u'QQ\u53f7', max_length=32, blank=True)
    phone = models.CharField(u'\u624b\u673a\u53f7', max_length=64, blank=True)
    email = models.EmailField(u'\u90ae\u7bb1', max_length=254, blank=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    objects = BkUserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'login_bkuser'

    @property
    def is_staff(self):
        return self.is_superuser

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_absolute_url(self):
        return '/users/%s/' % urlquote(self.email)

    def get_full_name(self):
        """
        Return the username plus the chinese name, with a space in between
        """
        full_name = '%s %s' % (self.username, self.chname)
        return full_name.strip()

    def get_short_name(self):
        """
        Return the chinese name for the user
        """
        return self.chname

    def email_user(self, subject, message, from_email = None):
        """
        Send an email to this User
        """
        send_mail(subject, message, from_email, [self.email])


class LoginLogManager(models.Manager):
    """
    User login log manager
    """

    def record_login(self, _user, _login_browser, _login_ip, host, app_id):
        try:
            self.model(user=_user, login_browser=_login_browser, login_ip=_login_ip, login_host=host, login_time=timezone.now(), app_id=app_id).save()
            return (True, u'\u8bb0\u5f55\u6210\u529f')
        except:
            return (False, u'\u7528\u6237\u767b\u5f55\u8bb0\u5f55\u5931\u8d25')


class Loignlog(models.Model):
    """
    User login log
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=u'\u7528\u6237')
    login_time = models.DateTimeField(u'\u767b\u5f55\u65f6\u95f4')
    login_browser = models.CharField(u'\u767b\u5f55\u6d4f\u89c8\u5668', max_length=200, blank=True, null=True)
    login_ip = models.CharField(u'\u7528\u6237\u767b\u5f55ip', max_length=50, blank=True, null=True)
    login_host = models.CharField(u'\u767b\u5f55HOST', max_length=100, blank=True, null=True)
    app_id = models.CharField('APP_ID', max_length=30, blank=True, null=True)
    objects = LoginLogManager()

    def __unicode__(self):
        return '%s(%s)' % (self.user.chname, self.user.username)

    class Meta:
        db_table = 'login_bklog'
        verbose_name = u'\u7528\u6237\u767b\u5f55\u65e5\u5fd7'
        verbose_name_plural = u'\u7528\u6237\u767b\u5f55\u65e5\u5fd7'


class BkToken(models.Model):
    """
    \xe7\x99\xbb\xe5\xbd\x95\xe7\xa5\xa8\xe6\x8d\xae
    """
    token = models.CharField(u'\u767b\u5f55\u7968\u636e', max_length=255, unique=True, db_index=True)
    is_logout = models.BooleanField(u'\u7968\u636e\u662f\u5426\u5df2\u7ecf\u6267\u884c\u8fc7\u9000\u51fa\u767b\u5f55\u64cd\u4f5c', default=False)
    inactive_expire_time = models.IntegerField(u'\u65e0\u64cd\u4f5c\u5931\u6548\u65f6\u95f4\u6233', default=0)

    def __uincode__(self):
        return self.token

    class Meta:
        db_table = 'login_bktoken'
        verbose_name = u'\u767b\u5f55\u7968\u636e'
        verbose_name_plural = u'\u767b\u5f55\u7968\u636e'
