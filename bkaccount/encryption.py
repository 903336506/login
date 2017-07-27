#Embedded file name: ./login/bkaccount/encryption.py
"""
\xe7\x99\xbb\xe5\xbd\x95\xe6\x80\x81\xe5\x8a\xa0\xe5\xaf\x86\xe6\x96\xb9\xe6\xb3\x95.

\xe4\xbd\xbf\xe7\x94\xa8AES\xe7\xae\x97\xe6\xb3\x95\xef\xbc\x8cECB\xe6\xa8\xa1\xe5\xbc\x8f
"""
import hashlib
import random
from base64 import urlsafe_b64encode, urlsafe_b64decode
from Crypto.Cipher import AES
from django.conf import settings

def pad(text, blocksize = 16):
    """
    PKCS#5 Padding
    """
    pad = blocksize - len(text) % blocksize
    return text + pad * chr(pad)


def unpad(text):
    """
    PKCS#5 Padding
    """
    pad = ord(text[-1])
    return text[:-pad]


def decrypt(ciphertext, key = '', base64 = True):
    """
    AES Decrypt
    """
    if not key:
        key = settings.SECRET_KEY
    if base64:
        ciphertext = urlsafe_b64decode(str(ciphertext + '=' * (4 - len(ciphertext) % 4)))
    data = ciphertext
    key = hashlib.md5(key).digest()
    cipher = AES.new(key, AES.MODE_ECB)
    return unpad(cipher.decrypt(data))


def encrypt(plaintext, key = '', base64 = True):
    """
    AES Encrypt
    """
    if not key:
        key = settings.SECRET_KEY
    key = hashlib.md5(key).digest()
    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = cipher.encrypt(pad(plaintext))
    if base64:
        ciphertext = urlsafe_b64encode(str(ciphertext)).rstrip('=')
    return ciphertext


def salt(length = 8):
    """
    \xe7\x94\x9f\xe6\x88\x90\xe9\x95\xbf\xe5\xba\xa6\xe4\xb8\xbalength \xe7\x9a\x84\xe9\x9a\x8f\xe6\x9c\xba\xe5\xad\x97\xe7\xac\xa6\xe4\xb8\xb2
    """
    aplhabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(map(lambda _: random.choice(aplhabet), range(length)))
