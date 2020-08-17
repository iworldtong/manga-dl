# Manga-dl
**[Manga-dl](https://github.com/iworldtong/manga-dl)** is a command line tool which helps you search and download comic from multiple sources.

Support for Mangabz、~~Manhuagui~~、Manhuabei and Manhuadb. See [supported sources](https://github.com/iworldtong/manga-dl#支持的漫画站点).

**Python3 Only. Python 3.7+ Recommended.**

[English](https://github.com/iworldtong/manga-dl/blob/master/README.en.md) | 中文文档

**[Manga-dl](https://github.com/iworldtong/manga-dl)**是一个基于Python3的命令行工具，可以从多个网站搜索和下载漫画，方便寻找漫画，解决不知道哪个网站有版权的问题。工具的本意是**聚合搜索**，API是从公开的网络中获得，**不是破解版**，也不能下载付费漫画。

欢迎提交插件支持更多漫画站点！插件写法参考`manga_dl/addons`中的文件。查看 [支持的漫画站点](#支持的漫画站点)。

**禁止将本工具用于商业用途**，如产生法律纠纷与本人无关，如有侵权，请联系我删除。

## 功能

- 使用解析js的方式爬取图片
- 支持 HTTP 和 SOCKS 代理
- 支持搜索结果去重和排序
- 支持搜索关键字高亮
- 支持多线程下载

> 注意：仅支持Python3，建议使用 **Python3.7 以上版本**

## 安装

使用pip安装（推荐，注意前面有一个`py`）：

```bash
$ pip install pymanga-dl
```

手动安装（最新）：

```bash
$ git clone https://github.com/iworldtong/manga-dl.git
$ cd manga-dl
$ python setup.py install
```

不安装直接运行：

```bash
$ git clone https://github.com/iworldtong/manga-dl.git
$ cd manga-dl
$ pip install -r requirements.txt
$ ./manga-dl

# 或 python manga-dl
```

在以下环境测试通过：

| 系统名称 | 系统版本 | Python版本 |
| -------- | -------- | ---------- |
| macOS    | 10.15    | 3.7.3      |

## 使用方式

建议先查看帮助

```
$ manga-dl --help
Usage: manga-dl [OPTIONS]

  Search and download comic from multiple sources.

  Example: manga-dl -k 辉夜大小姐

Options:
  --version             Show the version and exit.
  -k, --keyword TEXT    搜索关键字
  -u, --url TEXT        通过指定的漫画URL下载
  -s, --source TEXT     支持的数据源 ('+'分割): manhuabei+mangabz
  -n, --number INTEGER  搜索数量限制
  -o, --outdir TEXT     指定输出目录, 默认'./manga'
  -x, --proxy TEXT      指定代理（如socks5://127.0.0.1:1086）
  -v, --verbose         详细模式
  --nomerge             不对搜索结果列表排序和去重
  --help                Show this message and exit.
```

- 默认搜索`mangabz, manhuagui, manhuabei, manhuadb `，每个数量限制为5，保存目录为`./manga`
- 指定序号时可以使用`1-5 7 10`的形式
- 默认对搜索结果排序和去重
- 支持http代理和socks代理，格式形如`-x http://127.0.0.1:1087`或`-x socks5://127.0.0.1:1086`

示例：

<img src="https://res.cloudinary.com/dzu6x6nqi/image/upload/v1597549624/github/manga-dl_k-1.png">

## 支持的漫画站点

| 网站                                                         | 名称                                 | 简介                                                         |
| :----------------------------------------------------------- | ------------------------------------ | :----------------------------------------------------------- |
| <a href="https://www.mangabz.com/"><img src="https://css.mangabz.com/v202005281721/mangabz/images/logo_mangabz.png" height="50px"></a> | [Mangabz](https://www.mangabz.com/)  | 全網資源最全的在線漫畫、日本漫畫閱讀平臺。擁有時下最熱門的日漫作品，超快的更新速度，第一時間為你奉上極致的閱讀體驗。 |
| <a href="https://www.manhuagui.com/"><img src="https://qssily.oss-cn-hongkong.aliyuncs.com/img/manhuagui.png" height="50px"></a> | [漫画柜](https://www.manhuagui.com/) | 海量的国产漫画、日韩漫画、欧美漫画等丰富漫画资源，免费为漫画迷提供及时的更新、清新的界面和舒适的体验,努力打造属于漫画迷的漫画乐园。... |
| <a href="https://www.manhuagui.com/"><img src="https://res.cloudinary.com/dzu6x6nqi/image/upload/v1596637722/github/manhuabei_logo.png" height="50px"></a> | [漫画呗](https://www.manhuabei.com/) | 原名漫画堆、50漫画网，非商业性的二次元分享交流网站，不仅是一个提供宣传推广全世界各种不同漫画文化的分享交流平台，更致力于推动和发展国内原创动漫。 |
| <a href="https://www.manhuadb.com/"><img src="https://www.manhuadb.com/assets/www/img/logo.png" height="40px"></a> | [漫画DB](https://www.manhuadb.com/)  | 最专业的日本漫画大全资料库。所有漫画均可免费在线看，同时每部漫画都有丰富的资料，包括登场人物、用语、设定、改编作品及创作幕后等深层的内容。 |

欢迎提交插件支持更多漫画源！插件写法参考`manga_dl/addons`中的文件

## 更新记录

- 2020-08-15 完成v0.1版

## LICENSE

[MIT License](https://github.com/iworldtong/manga-dl/blob/master/LICENSE)

