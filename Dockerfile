FROM python:3.9

WORKDIR /app

COPY . .

RUN npm install
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# 设置环境变量，可以在运行容器时覆盖
ENV NACOS_SERVER_ADDR=localhost:8848
ENV NACOS_NAMESPACE=public
ENV SERVICE_NAME=xy-xianyuApi
ENV SERVICE_IP=localhost
ENV SERVICE_PORT=8000

# 启动FastAPI服务
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

# 构建命令：docker build -t xianyuapi .
# 运行命令：docker run -p 8000:8000 -e NACOS_SERVER_ADDR=nacos-server:8848 -e SERVICE_IP=container-ip xianyuapi