#!/usr/bin/env python
# -*- coding:utf-8 -*-



from manga_dl.addons import mangabz
from manga_dl import config

proxy = 'socks5://127.0.0.1:1086'
proxies = {"http": proxy, "https": proxy}
config.init()
config.set("proxies", proxies)


def test_mangabz():
    api = mangabz.Mangabz

    manga_urls = api.fetch_keyword("關于我轉生后成為史萊姆的那件事")
    assert manga_urls is not None

    manga = api.fetch_manga("https://www.mangabz.com/207bz/")
    assert manga is not None
