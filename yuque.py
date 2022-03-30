#!/usr/bin/env python3
# coding=utf-8


import requests
import yaml
from pathlib import Path

class YuQue:
    def __init__(self, token):
        self.token = token
        self.uri = 'https://www.yuque.com/api/v2'

    def _get(self, url, **kw):
        params = kw.get("params")
        headers = {
            "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Content-Type": "application/json",
            "X-Auth-Token": self.token
        }
        try:
            result = requests.get(url, params=params, headers=headers)
            return result
        except Exception as e:
            print("get请求错误: %s" % e)

    def get_doc(self, namespace, slug):
        url = self.uri + '/repos/' + namespace + '/docs/' + slug
        resp = self._get(url).json()
        if resp.get("status") == 401:
            print("Token Error")
        else:
            return resp['data']

    def get_info(self, namespace):
        url = self.uri + '/repos/' + namespace
        resp = self._get(url).json()

        tree_list = yaml.safe_load(resp['data']['toc_yml'])[1:]
        slug = []
        node = {}
        for tree in tree_list:
            if tree['level'] == 0 and tree['type'] == 'TITLE':
                node.update({tree['uuid']: Path(tree['title'])})
            elif tree['level'] == 0 and tree['type'] == 'DOC':
                slug.append({'path': str(Path()), 'title': tree['title'], 'slug': tree['url']})
            elif tree['level'] != 0 and tree['type'] == 'TITLE':
                p_path = node[tree['parent_uuid']]
                node.update({tree['uuid']: Path(p_path, tree['title'])})
            else:
                p_path = node[tree['parent_uuid']]
                node.update({tree['uuid']: Path(p_path)})
                slug.append({'path': str(node[tree['uuid']]), 'title': tree['title'], 'slug': tree['url']})
        return slug


if __name__ == '__main__':
    yq = YuQue('xxxxxxxxxxxxxxxxxxxx')
    print(yq.get_info('zjan/bwcmnq'))