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
                doc_list.append('\n' + new_line)
            elif '![' in line:
                new = line.split('#')[0] + ')'
                doc_list.append('\n' + new)
            elif '<br />' in line:
                new = line.replace('<br />', '\n')
                doc_list.append(new)
            else: 
                doc_list.append(line)
    except:
        pass
    
    return '\n'.join(doc_list)


if __name__ == '__main__':
    docs = "这是第一段文字    <br />这是第二段文字    <br />理论上他们应该是三个锻炼    \n> 这个是下个的测试内容了    \n\n![uTools_1648054722512.png](https://cdn.nlark.com/yuque/0/2022/png/243852/1648135776812-d200e74b-87c0-4a7c-b88d-b1718cb4dac1.png#clientId=uca452dff-1f61-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=u1bf174bd&margin=%5Bobject%20Object%5D&name=uTools_1648054722512.png&originHeight=857&originWidth=1693&originalType=binary&ratio=1&rotation=0&showTitle=false&size=73815&status=done&style=none&taskId=ub070ee11-f50f-429b-ac87-58326349b22&title=)\n> 感觉是需要调整的\n\n"
    print(hugo_lake_to_md(docs, 'test'))
    # with open('test.md', 'w') as f:
    #     md_doc = hugo_lake_to_md(docs, 'test')
    #     f.writelines(md_doc)
