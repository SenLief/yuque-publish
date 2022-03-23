#!/usr/bin/env python3
# coding=utf-8

import datetime
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

def hugo_lake_to_md(docs, title):
    date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")

    try:
        md_list = list(filter(lambda x: not x.startswith('<a') and x != "", docs.split('\n')))
        doc_list = []
        
        if md_list[0] == '```yaml':
            index = md_list.index('```')
            front = md_list[1:index]
            doc = md_list[index+1:]
            flag = []
            for line in front:
                if 'title:' in line and len(line) > 7:
                    flag.append('title')
                elif 'date:' in line and len(line) > 6:
                    flag.append('date')
                else:
                    pass
                
                doc_list.append(line)
            
            if 'title' not in flag:
                doc_list.append('title: ' + title)
            if 'date' not in flag:
                doc_list.append('date: ' + date)
            else:
                pass

            doc_list.insert(0, '---')
            doc_list.append('---')
        else:
            doc = md_list
            doc_list.insert(0, '---')
            doc_list.append('title: ' + title)
            doc_list.append('date: ' + date)
            doc_list.append('---')
        
        for line in doc:
            # 处理图片，后面会可选是否把图片拉到本地，现在可以使用图片。
            if '![' in line and '<br />' in line:
                new = line.split('#')[0] + ')'
                new_line = new.replace('<br />', '\n')
                doc_list.append(new_line)
            elif '![' in line:
                new = line.split('#')[0] + ')'
                doc_list.append(new)
            else: 
                doc_list.append(line)
    except:
        pass
    
    return '\n'.join(doc_list)


if __name__ == '__main__':
    docs = "```yaml\ndescription: \"Esmeralda\"\nfeatured_image: \"/images/esmeralda.jpg\"\ntags: []\ncategories: Story\n```\n下面主要是一些内容的测试\n"
    # print(lake_to_md(docs))
    print(hugo_lake_to_md(docs, '测试test'))
