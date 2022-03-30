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
    trees = yq.get_info(namespace)

    # 把目录写到本地，以便于更新和删除
    tree_path = Path(desdir, 'yuque.json')
    with open(tree_path, 'w+') as f:
        json.dump(trees, f, indent=6)
    
    # 遍历目录树
    for tree in trees:
        path = Path(desdir, tree['path'])
        if Path(path).exists():
                pass
        else:
            Path(path).mkdir(parents=True)
        doc = yq.get_doc(namespace, tree['slug'])
        file = Path(desdir, Path(tree['path']), tree['title'] + '.md')
        with open(file, 'w') as f:
            md_doc = hugo_lake_to_md(doc['body'], doc['title'])
            f.writelines(md_doc)
        print(doc['title'] + "已经下载")


@deploy
def publish_doc(slug, doc):
    # 获取目录列表
    yq = YuQue(token)
    trees = yq.get_info(namespace)
    tree_path = Path(desdir, 'yuque.json')
    with open(tree_path, 'w+') as f:
        json.dump(trees, f, indent=6)

    for tree in trees:
        path = Path(desdir, tree['path'])
        if Path(path).exists():
                pass
        else:
            Path(path).mkdir(parents=True)
        doc = yq.get_doc(namespace, tree['slug'])
        file = Path(desdir, Path(tree['path']), tree['title'] + '.md')
        with open(file, 'w') as f:
            md_doc = hugo_lake_to_md(doc['body'], tree['title'])
            f.writelines(md_doc)


@deploy
def delete_doc(slug):
    tree_path = Path(desdir, 'yuque.json')
    with open(tree_path, 'r') as f:
        trees = json.load(f)
    
    for tree in trees:
        if tree['slug'] == slug:
            path = Path(desdir, tree['path'], tree['title'] + '.md')
            Path(path).unlink()


@deploy
def update_doc(slug, doc):
    tree_path = Path(desdir, 'yuque.json')
    with open(tree_path, 'r') as f:
        trees = json.load(f)
    
    for tree in trees:
        if tree['slug'] == slug:
            path = Path(desdir, tree['path'])
            if Path(path).exists():
                pass
            else:
                Path(path).mkdir(parents=True)
                print("文档已被修改或移动，直接覆盖")
            file = Path(path, tree['title'] + '.md')
            with open(file, 'w') as f:
                md_doc = hugo_lake_to_md(doc, tree['title'], html=html)
                f.writelines(md_doc)
        else:
            pass

   
if __name__ == '__main__':
    # publish_doc('qt8h7t', '<a name=\"x9d6C\"></a>\n## 这篇文档只是用来测试的e\n\n', '这是一篇测试文档')
    # update_doc('qt8h7t', '<a name=\"x9d6C\"></a>\n## 更新了一遍文章\n\n', '这是一篇测试文档')
    # delete_doc('qt8h7t', '这是一篇测试文档')
    init_doc()    