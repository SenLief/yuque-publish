#!/usr/bin/env python3
# coding=utf-8

import os
import subprocess
import requests
import yaml
import json

from pathlib import Path

from yuque import YuQue
from lake2md import Doc


class Config:
    def __init__(self, prefix):
        try:
            pwd = Path(__file__).absolute()
            file_path = Path(pwd).parent / 'config.json'
            with open(file_path, 'r') as f:
                config = json.load(f)

            if prefix in config.keys():
                self.token = config[prefix]['token']
                self.namespace = config[prefix]['namespace']
                self.desdir = config[prefix]['desdir']
                self.workdir = config[prefix]['workdir']
                self.cmd = config[prefix]['cmd']
                self.conf = config[prefix]['hugo']
            else:
                print("配置不正确！")
        except OSError as e:
            print(e)

    def deploy(self):
        if self.cmd != '':
            os.chdir(self.workdir)
            return subprocess.Popen(self.cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8")
        else:
            print('没有命令可以执行')
        

def init_doc(prefix):
    config = Config(prefix)
    yq = YuQue(config.token)
    trees = yq.get_info(config.namespace)

    # 把目录写到本地，以便于更新和删除
    tree_path = Path(config.desdir, 'yuque.json')
    with open(tree_path, 'w+') as f:
        json.dump(trees, f, indent=6)
    
    # 遍历目录树
    for tree in trees:
        path = Path(config.desdir, tree['path'])
        if Path(path).exists():
                pass
        else:
            Path(path).mkdir(parents=True)
        doc = yq.get_doc(config.namespace, tree['slug'])
        docs = Doc(doc['body'], doc['title'], config.conf)
        if doc['format'] == 'lake':
            file = Path(config.desdir, Path(tree['path']), tree['title'] + '.md')
            with open(file, 'w') as f:
                md_doc = docs.lake_to_md()
                f.writelines(md_doc)
            print(doc['title'] + '---' + "已经下载")
        else:
            print(doc['title'] + '---' + "格式不支持跳过")



def publish_doc(slug, doc, title, prefix):
    config = Config(prefix)
    docs = Doc(doc, title, config.conf)
    # 获取目录列表
    yq = YuQue(config.token)
    trees = yq.get_info(config.namespace)
    tree_path = Path(config.desdir, 'yuque.json')
    with open(tree_path, 'w+') as f:
        json.dump(trees, f, indent=6)

    for tree in trees:
        if tree['slug'] == slug:
            path = Path(config.desdir, tree['path'])
            if Path(path).exists():
                    pass
            else:
                Path(path).mkdir(parents=True)
            file = Path(config.desdir, Path(tree['path']), tree['title'] + '.md')
            with open(file, 'w') as f:
                # md_doc = hugo_lake_to_md(doc, tree['title'], html=config.html)
                md_doc = docs.lake_to_md()
                f.writelines(md_doc)
            title = tree['title']
        else:
            pass
    
    config.deploy()
    print(f"知识库{config.namespace}发布了一遍名为<<{title}>>的文章并已部署！")


def delete_doc(slug, prefix):
    config = Config(prefix)
    tree_path = Path(config.desdir, 'yuque.json')
    with open(tree_path, 'r') as f:
        trees = json.load(f)
    
    for tree in trees:
        if tree['slug'] == slug:
            path = Path(config.desdir, tree['path'], tree['title'] + '.md')
            Path(path).unlink()
            title = tree['title']
    config.deploy()
    print(f"知识库{config.namespace}删除了一篇名为<<{title}>>的文章!")


def update_doc(slug, doc, title, prefix):
    config = Config(prefix)
    docs = Doc(doc, title, config.conf)
    tree_path = Path(config.desdir, 'yuque.json')
    with open(tree_path, 'r') as f:
        trees = json.load(f)
    
    for tree in trees:
        if tree['slug'] == slug:
            path = Path(config.desdir, tree['path'])
            if Path(path).exists():
                pass
            else:
                Path(path).mkdir(parents=True)
                print("文档已被修改或移动，直接覆盖")
            file = Path(path, tree['title'] + '.md')
            with open(file, 'w') as f:
                # md_doc = hugo_lake_to_md(doc, tree['title'], html=config.html)
                md_doc = docs.lake_to_md()
                f.writelines(md_doc)
            title = tree['title']
        else:
            pass
    config.deploy()
    print(f"知识库{config.namespace}更新了一篇<<{title}>>的文章！")

   
if __name__ == '__main__':
    # doc = "```yaml\ntags: [test, yuque]\n```\n> 这是引用\n\n这是文字\n<a name=\"p0MEK\"></a>\n# 这是H1\n这是h1文字\n<a name=\"FE8LE\"></a>\n## 这是H2\n这是h2<br />**这是加粗**<br />**_这是斜体_**<br />下面是列表\n\n- list1\n- list2\n- list3\n\n下面是有序列表\n\n1. 1list\n1. 2list\n1. 3list\n\n下面是表格\n\n| a | b | c |\n| --- | --- | --- |\n| 1 | 2 | 3 |\n| 4 | 5 | 6 |\n\n下面是图片<br />![uTools_1648054722512 (2).jpg](https://cdn.nlark.com/yuque/0/2022/jpeg/243852/1648913482476-284dd4f6-d81c-4320-ad54-e2f40e44ad5c.jpeg#clientId=u0c8c461d-2498-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=u75a9accd&margin=%5Bobject%20Object%5D&name=uTools_1648054722512%20%282%29.jpg&originHeight=857&originWidth=1693&originalType=binary&ratio=1&rotation=0&showTitle=false&size=73815&status=done&style=none&taskId=uad17c50f-f0a4-40e2-8a30-7c020adeb4a&title=)<br /> 下面是链接<br />[链接](http://www,baidu.com)<br />下面是代码\n```python\nimport this\n```\n`$ bash test.sh`这是行内代码<br />下面是b站<br />[点击查看【bilibili】](https://player.bilibili.com/player.html?bvid=BV1tq4y1e7RW)<br />下面是music<br />[点击查看【music163】](https://music.163.com/outchain/player?type=2&id=1420830402&auto=0&height=66)<br />下面是附件<br />[favicon_package_v0.16.zip](https://www.yuque.com/attachments/yuque/0/2022/zip/243852/1648913657004-5f256593-4400-4b63-a139-fdf0e5f3e6af.zip?_lake_card=%7B%22src%22%3A%22https%3A%2F%2Fwww.yuque.com%2Fattachments%2Fyuque%2F0%2F2022%2Fzip%2F243852%2F1648913657004-5f256593-4400-4b63-a139-fdf0e5f3e6af.zip%22%2C%22name%22%3A%22favicon_package_v0.16.zip%22%2C%22size%22%3A247603%2C%22type%22%3A%22application%2Fx-zip-compressed%22%2C%22ext%22%3A%22zip%22%2C%22status%22%3A%22done%22%2C%22taskId%22%3A%22ueddaf3ee-1665-4f3b-bafb-d74835d8b14%22%2C%22taskType%22%3A%22upload%22%2C%22id%22%3A%22u4f63386d%22%2C%22card%22%3A%22file%22%7D)<br />下面是导图<br />![](https://cdn.nlark.com/yuque/0/2022/jpeg/243852/1648914842615-69be76e4-6e4a-4bd4-965a-6f0ae1b77930.jpeg)<br />下面是文本绘图\n![](https://cdn.nlark.com/yuque/__puml/9f5560730e769f3fe0fe8387247e9beb.svg#lake_card_v2=eyJ0eXBlIjoicHVtbCIsImNvZGUiOiJAc3RhcnR1bWxcblA6IFBFTkRJTkdcblA6IFBlbmRpbmcgZm9yIHJlc3VsdFxuXG5OOiBOT19SRVNVTFRfWUVUXG5OOiBEaWQgbm90IHNlbmQgdGhlIEtZQyBjaGVjayB5ZXQgXG5cblk6IEFQUFJPVkVEXG5ZOiBLWUMgY2hlY2sgc3VjY2Vzc2Z1bFxuXG5SOiBSRUpFQ1RFRFxuUjogS1lDIGNoZWNrIGZvdW5kIHRoZSBhcHBsaWNhbnQncyBcblI6IGluZm9ybWF0aW9uIG5vdCBjb3JyZWN0IFxuXG5YOiBFWFBJUkVEXG5YOiBQcm9vZiBvZiBBZGRyZXNzIChQT0EpIHRvbyBvbGRcblxuWypdIC0tPiBOIDogQ2FyZCBhcHBsaWNhdGlvbiByZWNlaXZlZFxuTiAtLT4gUCA6IFN1Ym1pdHRlZCB0aGUgS1lDIGNoZWNrXG5QIC0tPiBZXG5QIC0tPiBSXG5QIC0tPiBYIDogUHJvb2Ygb2YgQWRkcmVzcyAoUE9BKSB0b28gb2xkXG5QIC0tPiBYIDogZXhwbGljaXRseSBieSBLWUNcblkgLS0-IFsqXVxuUiAtLT4gWypdXG5YIC0tPiBbKl1cbkBlbmR1bWwiLCJ1cmwiOiJodHRwczovL2Nkbi5ubGFyay5jb20veXVxdWUvX19wdW1sLzlmNTU2MDczMGU3NjlmM2ZlMGZlODM4NzI0N2U5YmViLnN2ZyIsImlkIjoiaXdUVFQiLCJtYXJnaW4iOnsidG9wIjp0cnVlLCJib3R0b20iOnRydWV9LCJjYXJkIjoiZGlhZ3JhbSJ9)"
    # publish_doc('hcz6g8', doc, 'content', 'bwcmnq')
    # time.sleep(3)
    # update_doc('ubuab7', '<a name=\"x9d6C\"></a>\n## 更新了一遍文章\n\n', 'uuid2')
    # time.sleep(3)
    # delete_doc('ubuab7', 'uuid2')
    init_doc(os.environ['PREFIX'])    
    # Config('bwcmnq')