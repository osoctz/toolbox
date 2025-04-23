import asyncio
from pubsub import pub

# 定义一个异步的监听器函数
async def async_listener(message):
    print(f"Async Listener received: {message}")
    await asyncio.sleep(10)  # 模拟异步操作（如 I/O、网络请求等）
    print("Async Listener completed processing.")

# 包装异步监听器函数以适配 PyPubSub
def listener_wrapper(message):
    asyncio.run(async_listener(message))

# 订阅事件
pub.subscribe(listener_wrapper, 'my_topic')

# 发布事件
print("Publishing event...")
pub.sendMessage('my_topic', message="Hello, Async PyPubSub!")
print("Published event...")