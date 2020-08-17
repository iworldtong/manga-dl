#!/usr/bin/env python
# -*- coding:utf-8 _*-
"""
@author: muketong
@file: utils.py
@time: 2020-08-15
"""
import os
import re
import requests
import platform
import threading
from tenacity import retry, wait_fixed, wait_exponential, retry_if_exception_type, stop_after_attempt


colors = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "pink": "\033[35m",
    "cyan": "\033[36m",

    "mangabz": "\033[92m",
    "manhuagui": "\033[94m",
    "manhuabei": "\033[91m",
    "manhuadb": "\033[96m",

    "highlight": "\033[93m",
    "error": "\033[31m",
}


def colorize(string, color):
    string = str(string)
    if color not in colors:
        return string
    if platform.system() == "Windows":
        return string
    return colors[color] + string + "\033[0m"


def validate_title(text):
    new_text = re.sub(r'[\\/:*?"<>|]', "", text)  
    return new_text


from PIL import Image
def img_verify(file): 
    is_valid = True
    if isinstance(file, (str, os.PathLike)):
        fileObj = open(file, 'rb')
    else:
        fileObj = file

    buf = fileObj.read()
    if buf[6:10] in (b'JFIF', b'Exif'): # jpg
        if not buf.rstrip(b'\0\r\n').endswith(b'\xff\xd9'):
            is_valid = False
    elif buf[1:4] in (b'PNG'):     # png
        if not buf.rstrip(b'\0\r\n').endswith(b'\xaeB`\x82'):
            is_valid = False
    else:        
        try:  
            Image.open(fileObj).verify() 
        except:  
            is_valid = False
            
    return is_valid


@retry(wait=wait_fixed(5), stop=stop_after_attempt(1000))
def retry_get(url, Referer_url=None, Cookie=None, headers=None, proxies=None):
    if headers is None:
        headers = {
            'User-Agent ' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0', 
        }
        if Referer_url:
            headers['Referer'] = Referer_url
        if Cookie:
            headers['Cookie'] = Cookie

    return requests.get(url, headers=headers, proxies=proxies) 


class DownloadThread(threading.Thread):
    def __init__(self, url, save_path, headers=None, proxies=None):
        threading.Thread.__init__(self)            
        self.url = url
        self.save_path = save_path
        self.headers = headers
        self.proxies = proxies

    def run(self):   
        self.download(self.url, self.save_path)

    def download(self, img_url, img_path, api=None):
        if os.path.exists(img_path):
            if img_verify(img_path):
                return
            else:
                os.remove(img_path)

        title, ext = os.path.splitext(img_path) 
        tmp_path = title + '.part'

        content = retry_get(img_url, headers=self.headers, proxies=self.proxies).content

        with open(tmp_path, 'wb') as f:
            f.write(content) 

        if img_verify(tmp_path):
            os.rename(tmp_path, img_path)
        else:
            os.remove(tmp_path)