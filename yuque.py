#!/usr/bin/env python3
# coding=utf-8


import requests
import yaml

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

    def get_doc_tree(self, namespace):
            url = self.uri + '/repos/' + namespace
            resp = self._get(url).json()

            tocs = yaml.safe_load(resp['data']['toc_yml'])[1:]

            node = []
            child_node = []
            t = [{"title":".", "slug": []}]

            for toc in tocs:
                if toc['level'] == 0 and toc['type'] == 'DOC':
                    t[0]['slug'].append(toc['url'])  
                elif toc['level'] == 0 and toc['type'] == 'TITLE':
                    node.append(toc)
                elif toc['level'] != 0:
                    child_node.append(toc)
                else:
                    pass
            
            for n in node:
                slug = []
                for cn in child_node:          
                    if cn['parent_uuid'] == n['uuid']:
                        slug.append(cn['url'])
                    else:
                        pass
                t.append(dict(title=n['title'], slug=slug))

            return t  