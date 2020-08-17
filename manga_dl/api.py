#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author: muketong
@file: api.py
@time: 2020-08-15
"""

import requests
from tenacity import retry, wait_fixed, wait_exponential, retry_if_exception_type, stop_after_attempt

from . import config
from .exceptions import RequestError, ResponseError, DataError


class MangaApi:
    # class property
    # 子类修改时使用deepcopy
    session = requests.Session()
    session.headers.update(config.get("fake_headers"))
    if config.get("proxies"):
        session.proxies.update(config.get("proxies"))
    session.headers.update({"referer": "http://www.google.com/"})


    @classmethod
    @retry(wait=wait_fixed(5), stop=stop_after_attempt(1000))
    def request(cls, url, method="GET", data=None):
        if method == "GET":
            resp = cls.session.get(url, params=data, timeout=7)
        else:
            resp = cls.session.post(url, data=data, timeout=7)
        if resp.status_code != requests.codes.ok:
            raise RequestError(resp.text)
        if not resp.text:
            raise ResponseError("No response data.")
        return resp
