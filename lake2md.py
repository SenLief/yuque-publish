#!/usr/bin/env python3
# coding=utf-8

import datetime
import re
import json
from pathlib import Path

# 通用的转换

date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")


class Doc:
    def __init__(self, doc, title, config):
        self.date = date
        self.title = title
        self.doc = doc
        self.conf = config


    def __sep_doc(self):
        if len(self.doc) > 1:
            if '<br />' in self.doc:
                d_list = self.doc.replace('<br />', '\n')
                md_list = list(filter(lambda x: not x.startswith('<a') and x != "", d_list.split('\n')))
            else:
                md_list = list(filter(lambda x: not x.startswith('<a') and x != "", self.doc.split('\n')))
            
            flag = md_list[0]
            if flag == '```yaml' or flag == '---':
                if flag == '```yaml':
                    end_index = md_list[1:].index('```') + 1
                elif flag == '---':
                    end_index = md_list[1:].index('---') + 1
                else:
                    print("error")
                front_list = (md_list[1:end_index])
                content_list = (md_list[end_index+1:])
            elif '`>' in md_list:
                # 私有的格式
                pass
            else:
                # 没有front,自动填充
                front_list = []
                content_list = md_list
        else:
            # 空文档
            front_list = []
            content_list = []
        return front_list, content_list

    def __front(self, front_list):
        front = []
        front.append(f'title: {self.title}')
        front.append(f'date: {self.date}')
        front.extend(front_list)
        if 'front' in self.conf:
            front_addon_list = self.conf['front']
            front.extend(front_addon_list)
        else:
            pass
        front.insert(0, '---')
        front.append('---')
        return front


    def __media(self, line):
        media_info = []
        p_cap = re.compile(r'\[.*]', re.I)
        media_cap = re.search(p_cap, line)[0].lstrip('[').rstrip(']')
        if ' ' in media_cap:
            media_cap = media_cap.replace(' ', '')
        else:
            pass
        media_info.append(media_cap)

        if 'svg' not in line:
            p_url = re.compile(r'https://cdn.nlark.com/yuque/\d/\d{4}/(png|jpeg|7z|zip|rar)/\d{6}/\w+-\w+-\w+-\w+-\w+-\w+.(png|jpeg|7z|zip|rar)', re.I)
            # p_cap = re.compile(r'\[.*]', re.I)
            media_url = re.search(p_url, line)[0]
            # media_cap = re.search(p_cap, line)[0].lstrip('[').rstrip(']')
            # if ' ' in media_cap:
            #     media_cap = media_cap.replace(' ', '')
            # else:
            #     pass
            # media_info.append(media_cap)
            media_info.append(media_url)
        else:
            p_m = re.compile(r'https://cdn.nlark.com/yuque/\w+/\w{32}\.svg')
            p_url = re.search(p_m, line)[0]
            media_info.append(p_url)
        return media_info


    def __advanced_media(self, line):

        if 'player.bilibili.com' in line:
            p_bv = re.compile(r'BV\w{10}')
            bv = re.search(p_bv, line)[0]
            if '&p=' in line:
                p_page = re.compile(r'&p=\d+&')
                page = re.search(p_page, line)[0].lstrip('&p=').rstrip('&')
                url = f'{{{{< bilibili {bv} {page} >}}}}'
            else:
                url = f'{{{{< bilibili {bv} >}}}}'
        elif 'music.163.com' in line:
            p_id = re.compile(r'&id=\d+&')
            pid = re.search(p_id, line)[0].lstrip('&id=').rstrip('&')
            print(pid)
            url = f'{{{{< music auto="https://music.163.com/#/song?id={pid}" >}}}}'
        elif 'ditu.amap.com' in line:
            # 功能未实现，主题不支持高德，经纬度坐标不同。
            pass
        else:
            url = line
        return url


    # def __text(self, line):
    #     if '<' in line:
    #         return line + '\n'
    #     else:
    #         return line


    def __generate_md(self, line):
        if '[' and ']' and 'https://cdn.nlark.com' in line :
            media_info = self.__media(line)
            if '![' in line and self.conf.get('shortcode', False):
                new_line = f'{{{{< image src={media_info[1]} caption={media_info[0]} >}}}}'
            elif self.conf.get('html', False):
                new_line = f'<img src={media_info[1]} alt={media_info[0]} referrerPolicy="no-referrer" />'
            else:
                new_line = f'![{media_info[0]}]({media_info[1]})'
        elif 'bilibili' or '163' in line:
            new_line = self.__advanced_media(line)
        elif line.startswith('>'):
            new_line = line + '\n'
        else:
            new_line = line
        
        return new_line

    
    def lake_to_md(self):
        front_list, content_list = self.__sep_doc()
        front_list = self.__front(front_list)
        content_list = list(map(self.__generate_md, content_list))
        return '\n'.join([*front_list, *content_list])
                

def hugo_lake_to_md(docs, title, html=False):
    date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    # markdown内容list
    doc_list = []

    if len(docs) > 1:
        # 处理换行以及不是markdown的内容
        if '<br />' in docs:
            d_list = docs.replace('<br />', '\n')
            md_list = list(filter(lambda x: not x.startswith('<a') and x != "", d_list.split('\n')))
        else:
            md_list = list(filter(lambda x: not x.startswith('<a') and x != "", docs.split('\n')))
  
    # 处理front matter
    # if len(md_list) != 0:
        flag = md_list[0]
        if flag == '```yaml' or flag == '---':
            if flag == '```yaml':
                end_index = md_list[1:].index('```') + 1
            elif flag == '---':
                end_index = md_list[1:].index('---') + 1
            else:
                print("error")


            f = []
            for line in md_list[1:end_index]:
                if 'title:' in line and len(line) > 7:
                    f.append('title')
                elif 'date:' in line and len(line) > 6:
                    f.append('date')
                else:
                    pass
                
                doc_list.append(line)
            
            if 'title' not in f:
                doc_list.append('title: ' + title)
            if 'date' not in f:
                doc_list.append('date: ' + date)
            else:
                pass

            doc_list.insert(0, '---')
            doc_list.append('---')
            content_list = md_list[end_index+1:]
        else:
            doc_list.insert(0, '---')
            doc_list.append('title: ' + title)
            doc_list.append('date: ' + date)
            doc_list.append('---')
            content_list = md_list
    else:
        print("空文档")
        doc_list.insert(0, '---')
        doc_list.append('title: ' + title)
        doc_list.append('date: ' + date)
        doc_list.append('---')
        return '\n'.join(doc_list)

    # 处理图片
    p = re.compile(r'https://cdn.nlark.com/yuque/\d/\d{4}/(png|jpeg|7z|zip|rar)/\d{6}/\w+-\w+-\w+-\w+-\w+-\w+.(png|jpeg|7z|zip|rar)', re.I)

    for line in content_list:
        if '![' in line:
            img_url = re.search(p, line)[0]
            if html:
                doc_list.append('\n')
                doc_list.append(f'<img src={img_url} referrerPolicy="no-referrer" />')
                doc_list.append('\n')
            else:
                doc_list.append('\n')
                doc_list.append(f'![]({img_url})')
                doc_list.append('\n')
        elif line.startswith('<'):
            doc_list.append(line)
            doc_list.append('\n')
        else:
            doc_list.append(line)
    
    return '\n'.join(doc_list)


if __name__ == '__main__':
    docs =  "![uTools_1648054722512 (2).jpg](https://cdn.nlark.com/yuque/0/2022/jpeg/243852/1648833212606-f0abe9b7-8b60-4b8c-8700-a1e344ad33ab.jpeg#clientId=u997629aa-be97-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=u768d5c67&margin=%5Bobject%20Object%5D&name=uTools_1648054722512%20%282%29.jpg&originHeight=857&originWidth=1693&originalType=binary&ratio=1&rotation=0&showTitle=false&size=73815&status=done&style=none&taskId=u257d7075-d7fa-4b12-8792-b028fc6384f&title=)<br />[favicon_package_v0.16.zip](https://www.yuque.com/attachments/yuque/0/2022/zip/243852/1648833237057-bdee5e03-9652-4328-8e24-c88f88eaf488.zip?_lake_card=%7B%22src%22%3A%22https%3A%2F%2Fwww.yuque.com%2Fattachments%2Fyuque%2F0%2F2022%2Fzip%2F243852%2F1648833237057-bdee5e03-9652-4328-8e24-c88f88eaf488.zip%22%2C%22name%22%3A%22favicon_package_v0.16.zip%22%2C%22size%22%3A247603%2C%22type%22%3A%22application%2Fx-zip-compressed%22%2C%22ext%22%3A%22zip%22%2C%22status%22%3A%22done%22%2C%22taskId%22%3A%22u7bee152d-974f-4f68-be3a-d1d215849f8%22%2C%22taskType%22%3A%22upload%22%2C%22id%22%3A%22u61b54ec2%22%2C%22card%22%3A%22file%22%7D)\n\n| a | b | c |\n| --- | --- | --- |\n| 1 | 2 | 3 |\n|  |  |  |\n\n![](https://cdn.nlark.com/yuque/0/2022/jpeg/243852/1648833282053-08515385-fb75-452f-add8-11daea6460c1.jpeg)\n![](https://cdn.nlark.com/yuque/__puml/9f5560730e769f3fe0fe8387247e9beb.svg#lake_card_v2=eyJ0eXBlIjoicHVtbCIsImNvZGUiOiJAc3RhcnR1bWxcblA6IFBFTkRJTkdcblA6IFBlbmRpbmcgZm9yIHJlc3VsdFxuXG5OOiBOT19SRVNVTFRfWUVUXG5OOiBEaWQgbm90IHNlbmQgdGhlIEtZQyBjaGVjayB5ZXQgXG5cblk6IEFQUFJPVkVEXG5ZOiBLWUMgY2hlY2sgc3VjY2Vzc2Z1bFxuXG5SOiBSRUpFQ1RFRFxuUjogS1lDIGNoZWNrIGZvdW5kIHRoZSBhcHBsaWNhbnQncyBcblI6IGluZm9ybWF0aW9uIG5vdCBjb3JyZWN0IFxuXG5YOiBFWFBJUkVEXG5YOiBQcm9vZiBvZiBBZGRyZXNzIChQT0EpIHRvbyBvbGRcblxuWypdIC0tPiBOIDogQ2FyZCBhcHBsaWNhdGlvbiByZWNlaXZlZFxuTiAtLT4gUCA6IFN1Ym1pdHRlZCB0aGUgS1lDIGNoZWNrXG5QIC0tPiBZXG5QIC0tPiBSXG5QIC0tPiBYIDogUHJvb2Ygb2YgQWRkcmVzcyAoUE9BKSB0b28gb2xkXG5QIC0tPiBYIDogZXhwbGljaXRseSBieSBLWUNcblkgLS0-IFsqXVxuUiAtLT4gWypdXG5YIC0tPiBbKl1cbkBlbmR1bWwiLCJ1cmwiOiJodHRwczovL2Nkbi5ubGFyay5jb20veXVxdWUvX19wdW1sLzlmNTU2MDczMGU3NjlmM2ZlMGZlODM4NzI0N2U5YmViLnN2ZyIsImlkIjoib1JoUVUiLCJtYXJnaW4iOnsidG9wIjp0cnVlLCJib3R0b20iOnRydWV9LCJjYXJkIjoiZGlhZ3JhbSJ9)[点击查看【music163】](https://music.163.com/outchain/player?type=2&id=186453&auto=1&height=66\")\n\n"
    # print(hugo_lake_to_md(docs, 'test',  html=True))
    # print(front(docs, 'test', '```'))
    # with open('test.md', 'w') as f:
    #     md_doc = hugo_lake_to_md(docs, 'test')
    #     f.writelines(md_doc)
    file_path = Path(Path().cwd())/ 'config.json'
    with open(file_path, 'r') as f:
        config = json.load(f)
    doc = Doc(docs, 'test', config['blog'])
    print(doc.lake_to_md())
