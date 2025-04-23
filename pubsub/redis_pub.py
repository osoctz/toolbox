import json

import redis
import time

from langchain_core.documents import Document

# 连接到本地的Redis服务器
r = redis.Redis(host='localhost', port=6379, db=0)


def publish_message(channel, message):
    r.publish(channel, message)
    print(f"Published: {message} to {channel}")


if __name__ == "__main__":
    channel_name = 'knowledge_create'

    doc = Document(page_content="1111", metadata={"source": "1.docx"})
    # 每隔5秒发布一条消息
    # publish_message(channel_name, '{"knowledgeId":"222","status":1}')
    publish_message(channel_name, json.dumps(doc.model_dump()))
    publish_message("chat", "Hello from Redis!")
