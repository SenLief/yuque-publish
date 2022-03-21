#!/usr/bin/env python3
# coding=utf-8


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


if __name__ == '__main__':
    docs = '图片<br />![uTools_1647163085011.png](https://cdn.nlark.com/yuque/0/2022/png/243852/1647163094054-cfe7ca2e-2456-4b74-bdb2-6bdd5babb81a.png#clientId=u163a85fa-0b8e-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=u7b5cd496&margin=%5Bobject%20Object%5D&name=uTools_1647163085011.png&originHeight=428&originWidth=1357&originalType=binary&ratio=1&rotation=0&showTitle=false&size=11282&status=done&style=none&taskId=u3d420e32-f710-49b5-aaff-a5f073bed84&title=)<br />思维导图<br />表格\n\n| One | Two | Three |\n| --- | --- | --- |\n| 1 | 2 | 3 |\n| 4 | 5 | 6 |\n\n代码块\n```\nimport this\n```\n公式<br />![](https://cdn.nlark.com/yuque/__latex/ea60b71e5e52e982f610f1c7eb80da71.svg#card=math&code=fsdfs&id=Yoma3)\n\n'
    print(lake_to_md(docs))
