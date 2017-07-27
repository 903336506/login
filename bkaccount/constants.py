#Embedded file name: ./login/bkaccount/constants.py
"""
\xe5\x85\xa8\xe5\xb1\x80\xe5\xb8\xb8\xe9\x87\x8f
"""
import re
USERNAME_CHECK_PATTERN = re.compile('^[A-Za-z0-9]{4,20}$')
PASSWORD_CHECK_PATTERN = re.compile('^[A-Za-z0-9!@#\\$%\\^\\*\\(\\)-_\\+=]{4,20}$')
