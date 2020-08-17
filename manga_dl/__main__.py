#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author: muketong
@file: __init__.py
@time: 2020-08-15
"""

import sys
import re
import gettext
import click
import logging
import prettytable as pt

from . import config
from .utils import colorize
from .source import MangaSource

gettext.install("manga-dl", "locale")


def menu(mangas_list):
    # 创建table
    tb = pt.PrettyTable()
    tb.field_names = ["序号", "漫画", "状态", "最新话", "总章数", "来源"]
    # 遍历输出搜索列表
    for index, manga in enumerate(mangas_list):
        manga.idx = index
        tb.add_row(manga.row)
        # click.echo(manga.info)
    tb.align = "l"
    click.echo(tb)
    click.echo("")

    # 用户指定下载序号
    prompt = (
        _("请输入{下载序号}，支持形如 {numbers} 的格式，输入 {N} 跳过下载").format(
            下载序号=colorize(_("下载序号"), "yellow"),
            numbers=colorize("0 3-5 8", "yellow"),
            N=colorize("N", "yellow"),
        )
        + "\n >>"
    )

    choices = click.prompt(prompt)

    while not re.match(r"^((\d+\-\d+)|(\d+)|\s+)+$", choices):
        if choices.lower() == "n":
            return
        choices = click.prompt("%s%s" % (colorize(_("输入有误!"), "red"), prompt))

    click.echo("")
    selected_list = []
    for choice in choices.split():
        start, to, end = choice.partition("-")
        if end:
            selected_list += range(int(start), int(end) + 1)
        else:
            selected_list.append(int(start))

    for idx in selected_list:
        if idx < len(mangas_list):
            mangas_list[idx].download()


def run():
    ms = MangaSource()
    if config.get("keyword"):
        mangas_list = ms.search(config.get("keyword"), config.get("source").split())
        menu(mangas_list)
        config.set("keyword", click.prompt(_("请输入要搜索的漫画，或Ctrl+C退出") + "\n >>"))
        run()
    elif config.get("url"):
        manga = ms.single(config.get("url"))
        manga.download()
    else:
        return


@click.command()
@click.version_option()
@click.option("-k", "--keyword", help=_("搜索关键字"))
@click.option("-u", "--url", default="", help=_("通过指定的漫画URL下载"))
@click.option(
    "-s",
    "--source",
    # default="manhuabei",
    help=_("支持的数据源 ('+'分割): ") + "manhuabei+mangabz",
)
@click.option("-n", "--number", default=5, help=_("搜索数量限制"))
@click.option("-o", "--outdir", default="./manga", help=_("指定输出目录, 默认'./manga'"))
@click.option("-a", "--download_all", default=False, help=_("下载整部漫画，不进入章节选择界面"))
@click.option("-x", "--proxy", default="", help=_("指定代理（如socks5://127.0.0.1:1086）"))
@click.option("-v", "--verbose", default=False, is_flag=True, help=_("详细模式"))
@click.option("--nomerge", default=False, is_flag=True, help=_("不对搜索结果列表排序和去重"))

def main(
    keyword,
    url,
    source,
    number,
    outdir,
    download_all,
    proxy,
    verbose,
    nomerge,
):
    """
        Search and download comic from multiple sources.\n
        Supported sites: https://github.com/iworldtong/manga-dl#支持的漫画站点 \n
        Example: manga-dl -k 辉夜大小姐
        
    """
    if sum([bool(keyword), bool(url)]) != 1:
        keyword = click.prompt(_("搜索关键字") + "\n >>")

    # 初始化全局变量
    config.init()
    config.set("keyword", keyword)
    config.set("url", url)
    if source:
        config.set("source", source)
    config.set("number", min(number, 50))
    config.set("outdir", outdir)
    config.set("download_all", download_all)
    config.set("verbose", verbose)
    config.set("nomerge", nomerge)
    if proxy:
        proxies = {"http": proxy, "https": proxy}
        config.set("proxies", proxies)

    level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] %(levelname)-8s | %(name)s: %(msg)s ",
        datefmt="%H:%M:%S",
    )

    try:
        run()
    except (EOFError, KeyboardInterrupt):
        sys.exit(0)


if __name__ == "__main__":
    main()
