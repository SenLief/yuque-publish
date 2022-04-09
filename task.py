#!/usr/bin/env python3
# coding=utf-8

import os
import subprocess
import requests
import yaml
import json
import sys

from pathlib import Path
from loguru import logger

from yuque import YuQue
from lake2md import lake_to_md
from dotenv import dotenv_values

user_config = dotenv_values(".env")

class Config:
    def __init__(self, prefix):
        try:
            pwd = Path(__file__).absolute()
            file_path = Path(pwd).parent / 'config.json'
            logger.info(file_path)
            with open(file_path, 'r') as f:
                config = json.load(f)

            if prefix in config.keys():
                self.token = config[prefix]['token']
                # self.namespace = config[prefix]['token']
                self.basedir = config[prefix]['basedir']
                self.desdir = Path(self.basedir, config[prefix]['desdir'])
                self.workdir = Path(self.basedir, config[prefix]['workdir'])
                self.cmd = config[prefix]['cmd']
                self.conf = config[prefix]['hugo']
            else:
                logger.debug("配置不正确")
        except OSError as e:
            logger.exception(e)

    def deploy(self):
        if self.cmd != '':
            os.chdir(self.workdir)
            return subprocess.Popen(self.cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8")
        else:
            logger.debug("命令为空")


def init_doc(prefix, namespace):
    config = Config(prefix)
    yq = YuQue(config.token)
    trees = yq.get_info(namespace)
    logger.debug("文档树的内容：{}", trees)

    # 把目录写到本地，以便于更新和删除
    tree_path = Path(config.desdir, prefix + '.json')
    with open(tree_path, 'w+') as f:
        json.dump(trees, f, indent=6)
    
    # 遍历目录树
    for tree in trees:
        path = Path(config.desdir, tree['path'])
        if Path(path).exists():
                pass
        else:
            Path(path).mkdir(parents=True, exist_ok=True)
        doc = yq.get_doc(namespace, tree['slug'])
        if doc['format'] == 'lake':
            file = Path(config.desdir, Path(tree['path']), tree['title'] + '.md')
            with open(file, 'w') as f:
                md_doc = lake_to_md(doc['body'], doc['title'])
                f.writelines(md_doc)
            logger.info("{}---已经下载", doc['title'])
        else:
            logger.info("{doc_title}的格式为{doc_format}---格式不支持跳过", doc_title=doc['title'], doc_format=doc['format'])


def init_config(token, prefix):
    pwd = Path(__file__).absolute()
    file_path = Path(pwd).parent / 'config.json'
    with open(file_path, 'r') as f:
        config = json.load(f)
    
    basedir = user_config.get('BASEDIR', Path.home())
    desdir = Path(basedir, prefix, user_config.get('DESDIR', 'content'))
    workdir = Path(basedir, prefix)
    if workdir.exists():
        os.chdir(workdir)
    else:
        workdir.mkdir(parents=True, exist_ok=True)
        os.chdir(workdir)
    subprocess.call("hugo new site .",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8")
    desdir.mkdir(parents=True, exist_ok=True)
    conf = {
        prefix: {
            "token": token,
            "basedir": str(basedir),
            "desdir": str(desdir),
            "workdir": str(workdir),
            "cmd": "hugo",
            "hugo": {
                "html": True,
                "shortcode": False
            } 
        }
    }

    if prefix not in config:
        config.update(conf)
        logger.debug(config)
        with open(file_path, 'w') as f:
            json.dump(config, f, indent = 6)
        logger.debug("{}已经添加到配置", prefix)
    else:
        logger.debug("{}已经存在了", prefix)



def publish_doc(slug, doc, title, prefix, namespace):
    config = Config(prefix)
    # 获取目录列表
    yq = YuQue(config.token)
    trees = yq.get_info(namespace)
    tree_path = Path(config.desdir, prefix + '.json')
    with open(tree_path, 'w+') as f:
        json.dump(trees, f, indent=6)

    for tree in trees:
        if tree['slug'] == slug:
            path = Path(config.desdir, tree['path'])
            if Path(path).exists():
                    pass
            else:
                Path(path).mkdir(parents=True)
            doc = yq.get_doc(namespace, tree['slug'])
            file = Path(config.desdir, Path(tree['path']), tree['title'] + '.md')
            with open(file, 'w') as f:
                # md_doc = hugo_lake_to_md(doc, tree['title'], html=config.html)
                md_doc = lake_to_md(doc['body'], tree['title'])
                f.writelines(md_doc)
            title = tree['title']
        else:
            pass
    
    config.deploy()
    logger.info("知识库{}发布了一遍名为<<{}>>的文章并已部署！", namespace, title)


def delete_doc(slug, prefix, namespace):
    config = Config(prefix)
    tree_path = Path(config.desdir, prefix + '.json')
    with open(tree_path, 'r') as f:
        trees = json.load(f)
    
    for tree in trees:
        if tree['slug'] == slug:
            path = Path(config.desdir, tree['path'], tree['title'] + '.md')
            Path(path).unlink()
            title = tree['title']
    config.deploy()
    logger.info("知识库{}删除了一篇名为<<{}>>的文章!", namespace, title)


def update_doc(slug, doc, title, prefix, namespace):
    config = Config(prefix)
    yq = YuQue(config.token)
    tree_path = Path(config.desdir, prefix + '.json')
    with open(tree_path, 'r') as f:
        trees = json.load(f)
    
    for tree in trees:
        if tree['slug'] == slug:
            path = Path(config.desdir, tree['path'])
            if Path(path).exists():
                pass
            else:
                Path(path).mkdir(parents=True)
                logger.debug("文档已被修改或移动，直接覆盖")
            file = Path(path, tree['title'] + '.md')
            doc = yq.get_doc(namespace, tree['slug'])
            with open(file, 'w') as f:
                md_doc = lake_to_md(doc['body'], tree['title'])
                f.writelines(md_doc)
            title = tree['title']
        else:
            pass
    config.deploy()
    logger.info("知识库{}更新了一篇<<{}>>的文章！", namespace, title)

   
if __name__ == '__main__':
    # init_doc('zjan-bwcmnq') 
    init_config('cccc', 'abcd')   