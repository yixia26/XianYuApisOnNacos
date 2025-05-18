import os

# Nacos配置
NACOS_CONFIG = {
    "server_addr": os.getenv("NACOS_SERVER_ADDR", "127.0.0.1:8848"),
    "namespace": os.getenv("NACOS_NAMESPACE", "dev"),
    "username": os.getenv("NACOS_USERNAME", "nacos"),
    "password": os.getenv("NACOS_PASSWORD", "nacos"),
}

# 服务配置
SERVICE_CONFIG = {
    "name": os.getenv("SERVICE_NAME", "xy-xianyuApi"),
    "ip": os.getenv("SERVICE_IP", "localhost"),
    "port": int(os.getenv("SERVICE_PORT", "8000")),
    "metadata": {
        "version": "1.0.0",
        "description": "闲鱼API服务"
    }
}

# API路径前缀
API_PREFIX = "/api/v1"