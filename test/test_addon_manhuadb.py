#!/usr/bin/env python
# -*- coding:utf-8 -*-



from manga_dl.addons import manhuadb
from manga_dl import config

proxy = 'socks5://127.0.0.1:1086'
proxies = {"http": proxy, "https": proxy}
config.init()
config.set("proxies", proxies)



def test_manhuadb():
    api = manhuadb.Manhuadb

    manga_urls = api.fetch_keyword("jojo")
    assert manga_urls is not None

    manga = api.fetch_manga("https://www.manhuadb.com/manhua/147/")
    assert manga is not None
