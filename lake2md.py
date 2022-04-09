#!/usr/bin/env python3
# coding=utf-8

import datetime
import re

from loguru import logger


date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
# logger.add('test.log', format="{time} {level} {message}", level="INFO")

def get_pic(line):
    p_cap = re.compile(r'\[.*]', re.I)
    media_cap = re.search(p_cap, line)[0].lstrip('[').rstrip(']')
    if ' ' in media_cap:
        media_cap = media_cap.replace(' ', '')
    else:
        pass
    logger.debug("图片的信息：{media_cap}")
    if 'svg' in line:
        p_m = re.compile(r'https://cdn.nlark.com/yuque/\w+/\w{32}\.svg')
        media_url = re.search(p_m, line)[0]
        logger.debug("画板的地址：{media_url}")
    else:
        p_url = re.compile(r'https://cdn.nlark.com/yuque/\d/\d{4}/(png|jpeg)/\d{6}/\w+-\w+-\w+-\w+-\w+-\w+.(png|jpeg)', re.I)
        media_url = re.search(p_url, line)[0]
        logger.debug("图片的地址：{media_url}")
    return f'<img src="{media_url}" alt="{media_cap}" referrerPolicy="no-referrer" />  '


def get_attachment(line):
    if 'www.yuque.com/attachments' in line:
        logger.debug("附件的地址：{line}")
        p_cap = re.compile(r'\[.*]', re.I)
        attachment_cap = re.search(p_cap, line)[0].lstrip('[').rstrip(']')
        if ' ' in attachment_cap:
            attachment_cap = attachment_cap.replace(' ', '')
        else:
            pass
        attachment_format = 'zip|mp4|rar|html|7z|ai|mov|m4a|wmv|avi|flv|chm|wps|rtf|aac|htm|xhtml|rmvb|asf|m3u8|mpg|flac|dat|mkv|swf|m4v|webm|mpeg|mts|3gp|f4v|dv|m2t|mj2|mjpeg|mpe|ogg'
        p_url = re.compile(fr'https://www.yuque.com/attachments/yuque/\d/\d{{4}}/({attachment_format})/\d{{6}}/\w+-\w+-\w+-\w+-\w+-\w+.({attachment_format})', re.I)
        attachment_url = re.search(p_url, line)[0]
        attachment = f'[{attachment_cap}]({attachment_url})'
    else:
        attachment = line
    return attachment


def lake_to_md(doc, title):
    try:
        if '<br />' in doc:
            d_list = doc.replace('<br />', '  \n')
            md_list = list(filter(lambda x: not x.startswith('<a'), d_list.split('\n')))
        else:
            md_list = list(filter(lambda x: not x.startswith('<a'), doc.split('\n')))
    except IndexError as e:
        logger.info("文档为空，不渲染！")
        logger.error(e)
    logger.debug("文档的内容：{md_list}")    

    doc_list = []
    for line in md_list:
        if line.startswith('!['):
            img_url = get_pic(line)
            doc_list.append(img_url)
        elif 'www.yuque.com/attachments' in line:
            attachment_url = get_attachment(line)
            doc_list.append(attachment_url)
        else:
            doc_list.append(line)
    
    if doc_list[0] == '---':
        doc_list.insert(1, f"title: {title}")
        doc_list.insert(2, f"date: {date}")
    elif doc_list[0] == '```yaml':
        doc_list[0] = '---'
        index = doc_list[1:].index('```')
        doc_list[index+1] = '---'
        doc_list.insert(1, f"title: {title}")
        doc_list.insert(2, f"date: {date}")
    else:
        doc_list.insert(0, '---')
        doc_list.insert(1, f'title: {title}')
        doc_list.insert(2, f'date: {date}')
        doc_list.insert(3, '---')      
    
    logger.debug("Markdown的文档内容为：{}", '\n'.join(doc_list))
    return '\n'.join(doc_list)


if __name__ == '__main__':
    doc = "```yaml\ntags: [yuque, 防盗链]\n```\n> 语雀的图片现在已经开始防盗链了，这样就不好利用api同步到其他地方去，目前只能通过修改主题解决这个问题\n\n<a name=\"SbWqz\"></a>\n## Hugo修改主题\n`themes/<theme>/layouts/_default/baseof.html`  <br />修改这个文件添加几行代码  \n```html\n<head>\n    <meta name=\"referrer\" content=\"never\">\n</head>\n```\n<a name=\"ayC8Q\"></a>\n## 为每个图片链接添加属性\n> HTML的img标签可以通过添加属性来返回referer\n\n```html\n<img src=\"xxxxx\" referrerPolicy=\"no-referrer\"/>\n```\n \n<a name=\"YcyXB\"></a>\n## 最后还是需要把图片拉到本地才行。  \n![uTools_1648054722512.png](https://cdn.nlark.com/yuque/0/2022/png/243852/1648054731230-a4141c6f-be21-4906-bdca-f2443fceb0b6.png#clientId=u05a807ef-2cfd-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=ud2170015&margin=%5Bobject%20Object%5D&name=uTools_1648054722512.png&originHeight=857&originWidth=1693&originalType=binary&ratio=1&rotation=0&showTitle=false&size=73815&status=done&style=none&taskId=u6580d2c6-af27-4c2e-8012-e795162e884&title=)\n\n[语雀的图片防盗链问题](https://senlief.xyz/posts/语雀的图片防盗链问题.html)\n"
    print(lake_to_md(doc, 'test'))
