import json
import time

import redis

# 连接到本地的Redis服务器
r = redis.Redis(host='localhost', port=6379, db=0)
p = r.pubsub()


def my_handler(message):
    print('Received:', message['data'])
    d=json.loads(message['data'])

    print('Received:', d['knowledgeId'])


if __name__ == "__main__":
    channel_name = 'knowledge_create'

    # 订阅指定频道
    p.subscribe(**{channel_name: my_handler})

    # 开始监听
    thread = p.run_in_thread(sleep_time=0.001)

    # 保持程序运行以持续接收消息
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
        thread.stop()