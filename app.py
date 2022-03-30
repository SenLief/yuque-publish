from fastapi import FastAPI, BackgroundTasks
import uvicorn as uvicorn

from task import publish_doc, delete_doc, update_doc

app = FastAPI()

@app.post("/", status_code=200)
def yuque(data: dict, background_tasks: BackgroundTasks):
    req = data['data']   
    type = req['webhook_subject_type']
    format = req.get('format', '')
    if format == 'lake':
        if type == 'publish':
            background_tasks.add_task(publish_doc, req['slug'], req['body'])
        elif type == 'update':
            background_tasks.add_task(update_doc, req['slug'], req['body'])
        else:
            print("未知的请求TYPE")
        return {"msg": "收到了Webhook的请求！"}
    elif type == 'comment_create' and req['actor_id'] == req['commentable']['user_id']:
            background_tasks.add_task(delete_doc, req['commentable']['slug'])
    else:
        print("不支持的格式")
        return {"msg": "不支持解析的格式！"}


if __name__ == '__main__':
    uvicorn.run(app=app, host="127.0.0.1", port=8080)

