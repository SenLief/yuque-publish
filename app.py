#!/usr/bin/env python3
# coding=utf-8


import datetime
import random
import string
import requests
import uvicorn

from dotenv import dotenv_values
from pathlib import Path
from loguru import logger
from fastapi import FastAPI, BackgroundTasks

from task import publish_doc, delete_doc, update_doc, init_doc, init_config

config = dotenv_values(".env")
app = FastAPI()

@app.post("/yuque", status_code=200)
def yuque(data: dict, prefix: str, namespace: str, background_tasks: BackgroundTasks):
    # 添加日志
    pwd = Path(__file__).absolute()
    log_path  = Path(pwd).parent / 'logs'
    log_path.mkdir(parents=True, exist_ok=True)
    level = config.get('LEVEL', 'INFO')
    logger.add(Path(log_path, prefix + '.log'), format="{time} {level} {message}", rotation="1 MB", retention="10 days", level=level)
    logger.remove()

    if 'msgtype' in data and data['msgtype'] == 'markdown':
        logger.info("{}---下载已有文档", namespace.replace('-', '/'))
        background_tasks.add_task(init_doc, prefix, namespace.replace('-', '/'))
    else:
        # 获取webhook内容
        logger.debug("webhook的内容是{}", data)
        req = data['data']   
        type = req['webhook_subject_type']
        format = req.get('format', '')
        if format == 'lake':
            if type == 'publish':
                background_tasks.add_task(publish_doc, req['slug'], req['body'], req['title'], prefix, namespace.replace('-', '/'))
            elif type == 'update':
                background_tasks.add_task(update_doc, req['slug'], req['body'], req['title'], prefix, namespace.replace('-', '/'))
            else:
                logger.debug("未知的请求TYPE")
            return {"msg": "收到了Webhook的请求！"}
        elif type == 'comment_create' and req['actor_id'] == req['commentable']['user_id']:
                background_tasks.add_task(delete_doc, req['commentable']['slug'], prefix, namespace.replace('-', '/'))
        else:
            logger.debug("目前不支持的格式")
            return {"msg": "不支持解析的格式！"}


@app.get("/oauth2", status_code=200)
def oauth(state: str, code: str,background_tasks: BackgroundTasks):

    if state == 'yuque':
        url = 'https://www.yuque.com/oauth2/token'
        prefix = ''.join(random.sample(string.ascii_letters + string.digits, 5)) + str(datetime.datetime.now().strftime("%f"))
        try:
            data = {
                'client_id': config['CLIENT_ID'],
                'client_secret': config['CLIENT_SECRET'],
                'code': code,
                'grant_type': 'authorization_code'
            }
            logger.debug(data)
            resp = requests.post(url, data=data)
            resp = resp.json()

            background_tasks.add_task(init_config, resp['access_token'], prefix)
            return f'<html>认证成功：https://webhook.529213.xyz/yuque?prefix={prefix}</html>'
        except Exception as e:
            return '<html>认证失败请重试</html>'
            logger.error(e)


if __name__ == '__main__':
    uvicorn.run(app=app, host="127.0.0.1", port=8080., debug=True)

