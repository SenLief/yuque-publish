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
        p_url = re.compile(r'https://cdn.nlark.com/yuque/\d/\d{4}/(png|jpeg|7z|zip|rar)/\d{6}/\w+-\w+-\w+-\w+-\w+-\w+.(png|jpeg|7z|zip|rar)', re.I)
        p_cap = re.compile(r'\[.*]', re.I)
        media_url = re.search(p_url, line)[0]
        media_cap = re.search(p_cap, line)[0].lstrip('[').rstrip(']')
        if ' ' in media_cap:
            media_cap = media_cap.replace(' ', '')
        else:
            pass
        media_info.append(media_cap)
        media_info.append(media_url)
        return media_info


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
    docs =  '''```yaml\ntags: [语雀, 发布, 测试]\n```\n<a name=\"tqoYN\"></a>\n## 初衷\n一直有记录的习惯，有时候是随笔，有时候是记下备忘，有时候是分享，试过很多的工具，但是都无法满足。我们需要的不是那么Geek，就是简简单单的使用，语雀就是这样的一个工具，语雀的编辑体验给我的感觉很好，很有输入的欲望，一个好的编辑器才能让我们愉快的输入文字和记录文字。    \n\n语雀的也是可以分享的，我也会使用，但是语雀毕竟是在线的服务，虽然现在可以离线使用了，但是数据还是想保存到本地的，这样数据才会更有安全感。     \n\n语雀的导出格式是私有的格式，其他平台无法导入的，虽然提高了api，但是格式的问题也是不好解决。所以想自己写个简单的脚本来完成备份，同时也兼顾了发布的功能，推送到自己的博客上面来，以望做个备份的地方。\n<a name=\"o6aMw\"></a>\n## yuque-publish\n\n<a name=\"Q0DJG\"></a>\n### 类似的项目\n\n在Github上有类似的工具，比如yuque-hexo，但是我自己不用hexo的，同时yuque-hexo无法生成目录树的结构，如果用hexo的不妨看看这个项目，完成度高了很多，已经是很好用的级别了。\n\n<a name=\"SCjeE\"></a>\n### yuque-publish\n<a name=\"bkqkL\"></a>\n#### 特点\n\n- 利用语雀的webhook功能，实现自动部署。\n- 在语雀上完成`发布文档`、`更新文档`、`删除文档`功能\n- 保留目录树的结够，便于分类（目前只实现了一级的分组，语雀api目录树解析需要额外处理）\n- 搭配hugo静态博客更方便\n<a name=\"mrZFW\"></a>\n#### 缺点\n\n- 只是简单实现，只用于自己的备份的和发布，压力很小，代码只是实现逻辑，还没有优化。\n- 只能解析markdown文档，一些特性无法支持，比如思维导图，画板等无法实现。\n- 图片防盗链，现在只能依靠修改主题来实现\n- 目前只能解析1级的分组，更深的没有实现（觉得没什么必要）\n\n<a name=\"gPNOk\"></a>\n## 使用\n<a name=\"S3qJS\"></a>\n### 要求\n\n- Python3\n- Hugo生成的站点\n<a name=\"uJBex\"></a>\n### 安装yuque-publish\n```bash\n$ git clone https://github.com/SenLief/yuque-publish.git\n$ cd yuque-publish\n\n# 可以用虚拟环境来使用\n$ python3 -m venv ~/.venv\n$ source ~/.venv/bin/activate\n$ pip3 install -r requirements.txt\n```\n<a name=\"RmZNZ\"></a>\n### 配置ENV\n```bash\n$ vim .env\n\n# 输入并配置以下内容\nTOKEN='' #语雀的个人token(https://www.yuque.com/settings/tokens)\nNAMESPACE='' #语雀的namespace,例如`zjan/bwcmnq`,在url中可以看到。\nDESDIR='' #文档下载到哪个目录，可以按分组生成子文件夹\nWORKDIR='' #cmd工作目录，比如hugo静态生成的文件夹目录\nCMD='' #下载后可以自动执行的命令，比如`hugo`\n```\n<a name=\"S8cE9\"></a>\n### 初始化文档\n> 如果语雀中已经有相应的文档，需要备份和发布，可以先初始化文档，会把已有的文档下载到上面的DESDIR目录，请注意配置好Front matter，要不无法生成，另外无法获取非markdown的内容。    \n\n```bash\n# 下载已有内容到DESDIR，比如hugo的content目录\n$ python3 task.py\n```\n<a name=\"FmFl3\"></a>\n### 启动http server服务器监听webhook请求\n> 建议反代IP:Port    \n\n```bash\n$ python app.py\n\n# 默认监听8080端口，被占用的话就修改app.py随意的改。\n```\n<a name=\"GBpJG\"></a>\n## 语雀APP使用\n<a name=\"ymvUC\"></a>\n### 配置webhook机器人\n\n`知识库设置-更多设置-消息推送-其他渠道-填写信息-勾选新增评论，点击添加。`<br />![image.png](https://cdn.nlark.com/yuque/0/2022/png/243852/1648109835461-e1f77df0-6852-4596-9cf8-db69640e3915.png#clientId=ufe709b44-d297-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=374&id=ua23c72db&margin=%5Bobject%20Object%5D&name=image.png&originHeight=467&originWidth=1515&originalType=binary&ratio=1&rotation=0&showTitle=false&size=113805&status=done&style=none&taskId=u89a5c15c-8bbf-45da-9795-54fdd20d7ed&title=&width=1212)<br />![屏幕截图 2022-03-24 162005.png](https://cdn.nlark.com/yuque/0/2022/png/243852/1648110209170-dc3ee404-400e-4208-a6ec-0e6a2b6dbad0.png#clientId=ufe709b44-d297-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=uc1f7b601&margin=%5Bobject%20Object%5D&name=%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE%202022-03-24%20162005.png&originHeight=802&originWidth=1405&originalType=binary&ratio=1&rotation=0&showTitle=false&size=55007&status=done&style=none&taskId=u669c7eb5-dd75-45a5-90f7-27868c5725a&title=)\n> 可以点击一下测试，服务器会收到一个请求。\n\n<a name=\"cGHqa\"></a>\n### 知识库目录管理\n> 目前只支持一级的分组所以不要有2级分组，有也没用，分组太多，太乱了。    \n> 注意：是分组，不是文档下的创建子文档，子文档不会生成目录树。          \n\n\n`首页-目录管理-新建分组`（我基本上就是分组来分类的）           <br />![image.png](https://cdn.nlark.com/yuque/0/2022/png/243852/1648110473154-6eefa751-cd9c-4ff9-8ac8-75e8897b6ebc.png#clientId=ufe709b44-d297-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=540&id=u140ccb44&margin=%5Bobject%20Object%5D&name=image.png&originHeight=675&originWidth=1805&originalType=binary&ratio=1&rotation=0&showTitle=false&size=60801&status=done&style=none&taskId=udd9e1179-5fe1-4032-9077-20e884c7744&title=&width=1444)\n\n> 没有在分组中的文档会在DESDIR的根目录，有分组的就是在DESDIR/分组/文档     \n\n\n**目录树**\n```\n$DESDIR\n  - doc1\n  - doc2\n  - group1\n    - doc3\n    - doc4\n  - group2\n    - doc5\n    - doc6\n```\n<a name=\"vxwib\"></a>\n### 管理文档\n<a name=\"gXssh\"></a>\n#### 发布文档\n> 需要关闭 自动发布的功能，自动发布的功能不能触发webhook推送。\n\n1. Front Matter\n   1. 注意：Front matter为`yaml`格式，不过由于直接使用`---`太丑了，所以我使用了代码块作为Front matter，代码块的语言选择`yaml`。front代码块必须是所有代码块的最前面，务必保证`yaml`语法没有问题\n   1. ![image.png](https://cdn.nlark.com/yuque/0/2022/png/243852/1648110931030-2e7af4c5-af73-429e-ab36-71d24d75643c.png#clientId=ufe709b44-d297-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=115&id=u8bfc32dd&margin=%5Bobject%20Object%5D&name=image.png&originHeight=144&originWidth=949&originalType=binary&ratio=1&rotation=0&showTitle=false&size=8599&status=done&style=none&taskId=u51af5f82-590a-413d-9a27-373ea4c9c8e&title=&width=759.2)\n   1. Front matter可以忽略`title`和`date`可以自动添加\n2. 书写内容\n   1. 内容尽量为markdown的格式支持的\n   1. 不支持的内容可能会尝试转换，比如后续可能会添加`引用语雀内容`、`嵌入第三方视频`这两个常用的。\n3. 点击发布\n\n<a name=\"dwY69\"></a>\n#### 更新文档\n\n1. 和发布相同，选择已有文档修改即可。\n1. 记得最后点击更新，触发推送。\n<a name=\"lAiw2\"></a>\n#### 删除文档\n> 语雀没有提供删除的推送功能，所以说需要利用已知的触发webhook，目前是利用新增评论来完成的，也可以利用把文档改为私有来删除，还没有完成这个功能\n\n1. 服务器保留备份，只是不生成静态文件\n   1. 只需要在Front matter中添加`draft: True`\n2. 服务器删除备份\n   1. 在文档下方的评论回复`#closed`，会删除服务器的备份。\n   1. 然后删除语雀文档即可\n   1. 后续看看有没有其他好的方案\n3. 删除语雀文档，服务器不删除\n   1. 比如hugo的默认布局文件`_index.md`，第一次发布后，就没用了。\n   1. 直接删除语雀文档就可以，直接删除不会触发webhook。\n<a name=\"K3fHn\"></a>\n## 已知问题\n\n1. 语雀图片防盗链\n   1. 目前只能是修改主题来处理，具体可以看[链接](https://senlief.xyz/posts/%E8%AF%AD%E9%9B%80%E7%9A%84%E5%9B%BE%E7%89%87%E9%98%B2%E7%9B%97%E9%93%BE%E9%97%AE%E9%A2%98/)\n   1. 后续会考虑讲图片拉到本地后替换链接\n   1. 上传到图床\n2. 渲染问题\n   1. hugo的markdown渲染很严格，所以编辑内容的时候一定要注意才行。\n   1. 尤其是换行的时候，可以空一行，要不不会换行。\n<a name=\"l2sJa\"></a>\n## 实践和效果\n`语雀：`[语雀文档的效果](https://www.yuque.com/zjan/blog)<br />`Blog：`[发布后部署的效果](https://senlief.xyz/posts/%E6%8A%8A%E8%AF%AD%E9%9B%80%E4%BD%9C%E4%B8%BA%E5%8D%9A%E5%AE%A2%E7%9A%84%E6%96%87%E6%A1%A3%E7%AE%A1%E7%90%86%E5%92%8C%E7%BC%96%E8%BE%91%E5%99%A8/)\n<a name=\"EIiFM\"></a>\n## TODO\n\n- 完善代码日志和出错\n- 图片处理\n- 解析错误\n\n'''
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
