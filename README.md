# 🐟 XianYuApis - 闲鱼第三方API集成库

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)
[![Python Version](https://img.shields.io/badge/nodejs-18%2B-blue)](https://nodejs.org/zh-cn/)

**✨ 非官方闲鱼开放API接口封装库，通过网络请求操作所有的闲鱼操作，提供安全可靠的闲鱼平台功能访问能力。**
**⚠️ 注意：如有侵权联系作者删除。**


| 模块       | 已实现                                                                             |
|----------|---------------------------------------------------------------------------------|
| 闲鱼PC | ✅ 闲鱼所有http接口（sign参数解密）    |
| 闲鱼PC | ✅ 闲鱼websockets私信ws协议（接收发消息，sign+base64+protobuf协议）      |


## 🚀 一些成品
- https://github.com/shaxiu/XianyuAutoAgent




## 🌟 核心特性

- RESTful API + WebSocket 双通道
- 独立功能组件即插即用
- 基于`asyncio`的全异步架构🚀

## 🛠️ 快速开始
### ⛳运行环境
- Python 3.7+
- Node.js 18+

### 🎯安装依赖
```
pip install -r requirements.txt
npm install
```

### 🎨配置文件
复制cookie到代码中（注意！登录闲鱼后的cookie才是有效的，不登陆没有用，不然怎么知道给谁发消息）
本项目为逆向闲鱼提供可靠的api访问闲鱼能力，env文件作者忘了放了，下个版本放进去


### 🚀运行项目
```
python XianyuAutoAsync.py
```

### 🗝️注意事项
- XianyuAutoAsync.py中的代码是接收发消息的主入口，可以根据自己的需求进行修改
- XianyuApis.py中的代码包含了api接口的模板，sign参数已经解密，可以根据自己的需求进行修改，添加其他的接口


## 🧸额外说明
1. 感谢star⭐和follow📰！不时更新
2. 作者的联系方式在主页里，有问题可以随时联系我
3. 可以关注下作者的其他项目，欢迎 PR 和 issue
4. 感谢赞助！如果此项目对您有帮助，请作者喝一杯奶茶~~ （开心一整天😊😊）
5. thank you~~~

<div align="center">
  <img src="./author/wx_pay.png" width="400px" alt="微信赞赏码"> 
  <img src="./author/zfb_pay.jpg" width="400px" alt="支付宝收款码">
</div>


## 📈 Star 趋势
<a href="https://www.star-history.com/#cv-cat/XianYuApis&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=cv-cat/XianYuApis&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=cv-cat/XianYuApis&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=cv-cat/XianYuApis&type=Date" />
 </picture>
</a>

# 闲鱼 API 服务

这是一个基于 FastAPI 的闲鱼 API 服务，提供闲鱼聊天、消息发送等功能，并注册到 Nacos 服务发现中心。

## 功能特点

- 创建闲鱼会话
- 发送闲鱼消息
- 创建聊天对话
- 自动回复功能
- 注册到 Nacos 服务发现中心

## 安装依赖

```bash
pip install -r requirements.txt
```

## 环境变量配置

可以通过环境变量配置服务参数：

- `NACOS_SERVER_ADDR`: Nacos 服务器地址，默认为 `localhost:8848`
- `NACOS_NAMESPACE`: Nacos 命名空间，默认为 `public`
- `NACOS_USERNAME`: Nacos 用户名，默认为 `nacos`
- `NACOS_PASSWORD`: Nacos 密码，默认为 `nacos`
- `SERVICE_NAME`: 服务名称，默认为 `xy-xianyuApi`
- `SERVICE_IP`: 服务 IP，默认为 `localhost`
- `SERVICE_PORT`: 服务端口，默认为 `8000`

## 运行服务

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

## Docker 部署

### 构建镜像

```bash
docker build -t xianyuapi .
```

### 运行容器

```bash
docker run -p 8000:8000 \
  -e NACOS_SERVER_ADDR=nacos-server:8848 \
  -e SERVICE_IP=container-ip \
  xianyuapi
```

## API 接口

### 创建会话

```
POST /api/v1/session/create
```

请求体:

```json
{
  "cookies_str": "你的闲鱼cookies字符串",
  "auto_reply": false
}
```

### 发送消息

```
POST /api/v1/message/send
```

请求体:

```json
{
  "session_id": "session_1",
  "to_id": "接收者ID",
  "item_id": "商品ID",
  "text": "要发送的消息"
}
```

### 创建聊天

```
POST /api/v1/chat/create
```

请求体:

```json
{
  "session_id": "session_1",
  "to_id": "接收者ID",
  "item_id": "商品ID"
}
```

### 列出会话

```
GET /api/v1/session/list
```

### 删除会话

```
DELETE /api/v1/session/{session_id}
```

### 健康检查

```
GET /health
```

## 示例代码

```python
import requests

# 创建会话
cookies_str = "your_cookies_string"
response = requests.post(
    "http://localhost:8000/api/v1/session/create",
    json={"cookies_str": cookies_str, "auto_reply": False}
)
session_id = response.json()["session_id"]

# 发送消息
requests.post(
    "http://localhost:8000/api/v1/message/send",
    json={
        "session_id": session_id,
        "to_id": "receiver_id",
        "item_id": "item_id",
        "text": "Hello, World!"
    }
)
```
