import multiprocessing

# 监听端口
bind = "0.0.0.0:8000"

# 工作进程数：CPU核心数 * 2 + 1
workers = multiprocessing.cpu_count() * 2 + 1

# 使用 uvicorn worker 解析
worker_class = "uvicorn.workers.UvicornWorker"

# 日志配置
loglevel = "info"
accesslog = "-"  # 输出到标准输出
errorlog = "-"

# 超时设置（秒），防止上传大文件或录音转写超时
timeout = 120
keepalive = 5
