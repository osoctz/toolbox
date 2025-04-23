import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from functools import wraps

from config import logger, UPLOAD_FOLDER, app_configs, WHITELIST_PATHS, TIME_WINDOW, REQUIRED_HEADERS
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
executor = ThreadPoolExecutor(10)

# 确保有一个文件夹用来保存上传的文件
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# 缓存存储 key 和访问时间戳
request_cache = {}

# # 每隔 5 秒执行一次
# schedule.every(5).seconds.do(job)
#
# # 创建并启动一个后台线程来运行调度器
# scheduler_thread = threading.Thread(target=run_scheduler)
# scheduler_thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
# scheduler_thread.start()


# 装饰器：用于控制日志记录频率
def log_with_throttle(key_func):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # 检查是否在白名单内
            if request.path in WHITELIST_PATHS:
                # 如果路径在白名单中，直接记录日志
                log_request()
                return f(*args, **kwargs)

            # 否则，检查缓存和时间窗口
            key = key_func()
            current_time = datetime.now()

            # 检查缓存中是否有该 key 的记录
            if key in request_cache:
                last_access_time = request_cache[key]
                # 如果当前时间在时间窗口内，则跳过日志记录
                if current_time - last_access_time < timedelta(seconds=TIME_WINDOW):
                    return f(*args, **kwargs)

            # 更新缓存中的访问时间
            request_cache[key] = current_time

            # 记录请求日志
            log_request()

            return f(*args, **kwargs)

        return wrapper

    return decorator


# 辅助函数：记录请求日志
def log_request():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    method = request.method
    path = request.path
    ip = request.remote_addr
    user_agent = request.user_agent.string
    # data = request.get_data(as_text=True)  # 请求体数据
    app_id = request.headers.get('X-App-Id')

    logger.info(
        f"Request: {timestamp} | IP: {ip} | Method: {method} | Path: {path} | User-Agent: {user_agent}")

    # add_log(path, user_agent, ip, method, timestamp, app_id)


@app.route('/')
def index():
    return "hi,llm!"


@app.route('/models/recog', methods=['POST'])
@log_with_throttle(lambda: request.remote_addr + request.path)
def model_recog():
    """
    模型识别
    :return:
    """
    headers = request.headers

    missing_headers = [header for header in REQUIRED_HEADERS if header not in [h[0] for h in headers]]
    if missing_headers:
        return jsonify({
            'statusCode': 400,
            'message': f"Missing required headers,{missing_headers}"
        })
    # 从请求头中获取 app_id，如果没有则使用默认值
    app_id = request.headers.get('X-App-Id')
    if app_id not in app_configs:
        return jsonify({
            'statusCode': 400,
            'message': f"Unknown app id:{app_id}"
        })

    logger.info(f"app_id: {app_id}")
    file = request.files['file']
    file_id = request.form.get('fileId', '')
    # type = int(request.form.get('type', '1'))
    task_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # add_task(app_id, task_id, file_id, 'PENDING', file_path)
    return jsonify({"statusCode": 200, "data": {"taskId": task_id}})


if __name__ == '__main__':
    """
    celery -A app.celery worker --loglevel=info
    """
    app.run(host='0.0.0.0', port=8080, debug=True)
