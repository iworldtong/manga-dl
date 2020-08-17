#!/usr/bin/env python
# -*- coding:utf-8 -*-



from manga_dl.addons import manhuabei
from manga_dl import config

config.init()

def test_manhuabei():
    api = manhuabei.Manhuabei

    manga_urls = api.fetch_keyword("进击的巨人")
    assert manga_urls is not None

    manga = api.fetch_manga("https://www.manhuabei.com/manhua/jinjidejuren/")
    assert manga is not None
