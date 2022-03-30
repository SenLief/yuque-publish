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
                self.html = config[prefix]['html']
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

        if doc['format'] == 'lake':
            file = Path(config.desdir, Path(tree['path']), tree['title'] + '.md')
            with open(file, 'w') as f:
                md_doc = hugo_lake_to_md(doc['body'], doc['title'])
                f.writelines(md_doc)
            print(doc['title'] + '---' + "已经下载")
        else:
            print(doc['title'] + '---' + "格式不支持跳过")



def publish_doc(slug, doc, prefix):
    config = Config(prefix)
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
                md_doc = hugo_lake_to_md(doc, tree['title'], html=config.html)
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


def update_doc(slug, doc, prefix):
    config = Config(prefix)
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
                md_doc = hugo_lake_to_md(doc, tree['title'], html=config.html)
                f.writelines(md_doc)
            title = tree['title']
        else:
            pass
    config.deploy()
    print(f"知识库{config.namespace}更新了一篇<<{title}>>的文章！")

   
if __name__ == '__main__':
    # publish_doc('ubuab7', '<a name=\"x9d6C\"></a>\n## 这篇文档只是用来测试的e\n\n', 'uuid2')
    # time.sleep(3)
    # update_doc('ubuab7', '<a name=\"x9d6C\"></a>\n## 更新了一遍文章\n\n', 'uuid2')
    # time.sleep(3)
    # delete_doc('ubuab7', 'uuid2')
    init_doc('uuid2')    