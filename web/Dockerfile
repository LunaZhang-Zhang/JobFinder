# 使用官方 Python 3.9 镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录(虚拟机的)
WORKDIR /app

# 复制当前目录下的所有文件到容器的 /app 目录
COPY . /app

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露 Flask 应用的端口（默认是 5000）
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# 运行 Flask 应用
CMD ["flask", "run", "--host=0.0.0.0"]