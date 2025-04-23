from locust import HttpUser, TaskSet, task, between, constant


class PaddleOCRTask(TaskSet):

    # 前置处理
    def on_start(self):
        print("开始调用")

    # 后置处理
    def on_stop(self):
        print("停止调用")

    @task(1)
    def test_ocr(self):
        """
        https://docs.python-requests.org/en/latest/user/quickstart/#post-a-multipart-encoded-file
        :return:
        """
        login_url = 'http://localhost:8998/paddle/ocr/ocr_page'
        # header = {
        #     'Content-Type': 'multipart/form-data',
        # }
        data = {'image': open('/xxx/1052_军官证图片_20230220_191196.png', 'rb')}
        r = self.client.post(login_url, name="image ocr", files=data)
        # print(r.json())
        assert r.json()['code'] == 1


class PaddleOCRFinish(HttpUser):
    """
    命令行参数说明: https://blog.csdn.net/IT_heima/article/details/115420319
                https://debugtalk.com/post/head-first-locust-user-guide/

    示例入门: https://www.cnblogs.com/xiaolintongxue1/p/16822504.html
    https://www.jianshu.com/p/6920d3bd9190
    """
    tasks = [PaddleOCRTask]
    # max_wait / min_wait: 每个用户执行两个任务间隔时间的上下限（毫秒），具体数值在上下限中随机取值，若不指定则默认间隔时间固定为1秒；
    min_wait = 0
    max_wait = 0
    # 设置每次请求间隔时间
    # wait_time = between(1, 1)
    # wait_time = constant(1)
    host = "http://127.0.0.1:8089"
