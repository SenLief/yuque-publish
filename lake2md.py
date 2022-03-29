#!/usr/bin/env python3
# coding=utf-8

import datetime
import re
# 通用的转换
def lake_to_md(docs):
    # 处理空行和块id
    md_list = list(filter(lambda x: not x.startswith('<a') and x != "", docs.split('\n')))

    # 处理一些特殊情况
    md_lists = []  
    for line in md_list:
        # 处理图片，后面会可选是否把图片拉到本地，现在可以使用图片。
        if '![' in line and '<br />' in line:
            new = line.split('#')[0] + ')'
            new_line = new.replace('<br />', '\n')
            md_lists.append(new_line)
        elif '![' in line:
            new = line.split('#')[0] + ')'
            md_lists.append(new)
        else: 
            md_lists.append(line)

    return '\n'.join(md_lists)


def hugo_lake_to_md(docs, title, html=False):
    date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")

    # 处理换行以及不是markdown的内容
    if '<br />' in docs:
        d_list = docs.replace('<br />', '\n')
        md_list = list(filter(lambda x: not x.startswith('<a') and x != "", d_list.split('\n')))
    else:
        md_list = list(filter(lambda x: not x.startswith('<a') and x != "", docs.split('\n')))

    # markdown内容list
    doc_list = []
    # 处理front matter
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

    # 处理图片
    p = re.compile(r'https://cdn.nlark.com/yuque\S+#', re.I)
    for line in content_list:
        if '![' in line:
            if html:
                img_url = re.search(p, line)[0].rstrip('#')
                doc_list.append('\n')
                doc_list.append(f'<img src={img_url} referrerPolicy="no-referrer" />')
                doc_list.append('\n')
            else:
                new = line.split('#')[0] + ')'
                doc_list.append('\n')
                doc_list.append(new)
                doc_list.append('\n')
        elif line.startswith('<'):
            doc_list.append(line)
            doc_list.append('\n')
        else:
            doc_list.append(line)
    
    return '\n'.join(doc_list)


if __name__ == '__main__':
    docs =  "```yaml\n\ntags: [tst]\n\n```\n\nsdfsadfsf\n"
    print(hugo_lake_to_md(docs, 'test',  html=True))
    # print(front(docs, 'test', '```'))
    # with open('test.md', 'w') as f:
    #     md_doc = hugo_lake_to_md(docs, 'test')
    #     f.writelines(md_doc)
