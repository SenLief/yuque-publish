#!/usr/bin/env python3
# coding=utf-8

import os
import subprocess
import requests
import yaml
import json
import functools

from pathlib import Path
from dotenv import dotenv_values

from yuque import YuQue
from lake2md import hugo_lake_to_md


try:
    config = dotenv_values(".env")
    token = config['TOKEN']
    desdir = config['DESDIR']
    namespace = config['NAMESPACE']
    cmd = config['CMD']
    workdir = config['WORKDIR']
    html = config['HTML']
except Exception as e:
    print(f"环境变量配置错误：{0}", e)


def deploy(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func1 = func(*args, **kwargs)
        dir = Path(workdir)
        if not Path(dir).exists():
            print("工作目录不存在")
        else:
            os.chdir(dir)
        subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8")
        return func1
    return wrapper


def init_doc():
    yq = YuQue(token)
    tree = yq.get_doc_tree(namespace)
    tree_path = Path(desdir, 'yuque.json')
    with open(tree_path, 'w+') as f:
        json.dump(tree, f, indent=6)
    
    for group in tree:
        for slug in group['slug']:
            path = Path(desdir, group['title'])
            if Path(path).exists():
                pass
            else:
                Path(path).mkdir(parents=True)
            doc = yq.get_doc(namespace, slug)
            file = Path(path, doc['title'] + '.md')
            with open(file, 'w') as f:
                md_doc = hugo_lake_to_md(doc['body'], doc['title'])
                f.writelines(md_doc)
            print(doc['title'] + "已经下载")


@deploy
def publish_doc(slug, doc, title):
    # 获取目录列表
    yq = YuQue(token)
    tree = yq.get_doc_tree(namespace)
    tree_path = Path(desdir, 'yuque.json')
    with open(tree_path, 'w+') as f:
        json.dump(tree, f, indent=6)

    # 找到slug在那个分组
    for group in tree:
        if slug in group['slug']:
            group_path = Path(group['title'])
        else:
            pass
    
    path = Path(desdir, group_path)
    if Path(path).exists():
        pass
    else:
        Path(path).mkdir(parents=True)
    file = Path(path, title + '.md')
    with open(file, 'w') as f:
        md_doc = hugo_lake_to_md(doc, title, html=html)
        f.writelines(md_doc)
 

@deploy
def delete_doc(slug, title):
    tree_path = Path(desdir, 'yuque.json')
    with open(tree_path, 'r') as f:
        tree = json.load(f)
    
    for group in tree:
        if slug in group['slug']:
            path = Path(desdir, group['title'], title + '.md')
            Path(path).unlink()
        else:
            pass
    


@deploy
def update_doc(slug, doc, title):
    tree_path = Path(desdir, 'yuque.json')
    with open(tree_path, 'r') as f:
        tree = json.load(f)
    
    for group in tree:
        if slug in group['slug']:
            path = Path(desdir, group['title'])
            if Path(path).exists():
                pass
            else:
                Path(path).mkdir(parents=True)
                print("文档已被修改或移动，直接覆盖")
            file = Path(path, title + '.md')
            with open(file, 'w') as f:
                md_doc = hugo_lake_to_md(doc, title, html=html)
                f.writelines(md_doc)
        else:
            pass

    
if __name__ == '__main__':
    # publish_doc('qt8h7t', '<a name=\"x9d6C\"></a>\n## 这篇文档只是用来测试的e\n\n', '这是一篇测试文档')
    # update_doc('qt8h7t', '<a name=\"x9d6C\"></a>\n## 更新了一遍文章\n\n', '这是一篇测试文档')
    # delete_doc('qt8h7t', '这是一篇测试文档')
    init_doc()    