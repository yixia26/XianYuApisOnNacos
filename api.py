import json
import asyncio
from typing import Dict, Optional, List

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uvicorn
from loguru import logger
import nacos
import websockets

from XianyuAutoAsync import XianyuLive
from config import NACOS_CONFIG, SERVICE_CONFIG, API_PREFIX

# 配置日志
logger.add("api.log", rotation="10 MB")

app = FastAPI(
    title="闲鱼API服务",
    description="提供闲鱼聊天、消息发送等功能的API服务",
    version="1.0.0"
)

# 存储活跃的XianyuLive实例
active_sessions = {}

# 初始化Nacos客户端
nacos_client = nacos.NacosClient(
    NACOS_CONFIG["server_addr"],
    namespace=NACOS_CONFIG["namespace"]
)

# 数据模型
class CookiesModel(BaseModel):
    cookies_str: str

class MessageModel(BaseModel):
    session_id: str
    to_id: str
    item_id: str
    text: str

class CreateChatModel(BaseModel):
    session_id: str
    to_id: str
    item_id: str

class SessionModel(BaseModel):
    cookies_str: str
    auto_reply: bool = False

# 注册服务到Nacos
def register_service():
    try:
        success = nacos_client.add_naming_instance(
            SERVICE_CONFIG["name"],
            SERVICE_CONFIG["ip"],
            SERVICE_CONFIG["port"],
            ephemeral=True,
            metadata=SERVICE_CONFIG["metadata"]
        )
        if success:
            logger.info(f"服务 {SERVICE_CONFIG['name']} 已成功注册到Nacos")
        else:
            logger.error(f"服务 {SERVICE_CONFIG['name']} 注册到Nacos失败")
    except Exception as e:
        logger.error(f"注册服务到Nacos时出错: {str(e)}")

# 后台任务：启动自动回复
async def start_auto_reply(session_id: str):
    try:
        if session_id in active_sessions:
            xianyu_live = active_sessions[session_id]["instance"]
            logger.info(f"启动自动回复服务，会话ID: {session_id}")
            await xianyu_live.main()
    except Exception as e:
        logger.error(f"自动回复服务出错: {str(e)}")
        if session_id in active_sessions:
            active_sessions[session_id]["auto_reply"] = False

@app.on_event("startup")
async def startup_event():
    register_service()
    logger.info("闲鱼API服务已启动")

@app.on_event("shutdown")
async def shutdown_event():
    # 关闭所有活跃的会话
    for session_id, session_data in active_sessions.items():
        if session_data["auto_reply"]:
            # 这里应该有一个方法来优雅地关闭WebSocket连接
            logger.info(f"关闭会话: {session_id}")
    logger.info("闲鱼API服务已关闭")

@app.post(f"{API_PREFIX}/session/create", response_model=Dict)
async def create_session(session: SessionModel, background_tasks: BackgroundTasks):
    """创建一个新的闲鱼会话"""
    try:
        session_id = f"session_{len(active_sessions) + 1}"
        xianyu_live = XianyuLive(session.cookies_str)
        
        active_sessions[session_id] = {
            "instance": xianyu_live,
            "cookies_str": session.cookies_str,
            "auto_reply": session.auto_reply
        }
        
        # 如果需要自动回复，启动后台任务
        if session.auto_reply:
            background_tasks.add_task(start_auto_reply, session_id)
            
        return {
            "status": "success",
            "session_id": session_id,
            "message": "会话创建成功"
        }
    except Exception as e:
        logger.error(f"创建会话失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建会话失败: {str(e)}")

@app.post(f"{API_PREFIX}/message/send", response_model=Dict)
async def send_message(message: MessageModel):
    """发送单条消息"""
    try:
        if message.session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        xianyu_live = active_sessions[message.session_id]["instance"]
        await xianyu_live.send_msg_once(message.to_id, message.item_id, message.text)
        
        return {
            "status": "success",
            "message": "消息发送成功"
        }
    except Exception as e:
        logger.error(f"发送消息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"发送消息失败: {str(e)}")

@app.post(f"{API_PREFIX}/chat/create", response_model=Dict)
async def create_chat(chat: CreateChatModel):
    """创建聊天会话"""
    try:
        if chat.session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        xianyu_live = active_sessions[chat.session_id]["instance"]
        
        # 创建一个临时的WebSocket连接
        headers = {
            "Cookie": active_sessions[chat.session_id]["cookies_str"],
            "Host": "wss-goofish.dingtalk.com",
            "Connection": "Upgrade",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Origin": "https://www.goofish.com",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        
        async with websockets.connect(xianyu_live.base_url, extra_headers=headers) as websocket:
            await xianyu_live.init(websocket)
            await xianyu_live.create_chat(websocket, chat.to_id, chat.item_id)
            
            return {
                "status": "success",
                "message": "聊天会话创建成功"
            }
    except Exception as e:
        logger.error(f"创建聊天会话失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建聊天会话失败: {str(e)}")

@app.get(f"{API_PREFIX}/session/list", response_model=Dict)
async def list_sessions():
    """列出所有活跃的会话"""
    try:
        sessions = []
        for session_id, session_data in active_sessions.items():
            sessions.append({
                "session_id": session_id,
                "auto_reply": session_data["auto_reply"]
            })
            
        return {
            "status": "success",
            "sessions": sessions
        }
    except Exception as e:
        logger.error(f"获取会话列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取会话列表失败: {str(e)}")

@app.delete(f"{API_PREFIX}/session/{{session_id}}", response_model=Dict)
async def delete_session(session_id: str):
    """删除会话"""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 如果有自动回复任务，应该停止它
        active_sessions.pop(session_id)
        
        return {
            "status": "success",
            "message": f"会话 {session_id} 已删除"
        }
    except Exception as e:
        logger.error(f"删除会话失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除会话失败: {str(e)}")

@app.get("/health", response_model=Dict)
async def health_check():
    """健康检查接口"""
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(
        "api:app", 
        host="0.0.0.0", 
        port=SERVICE_CONFIG["port"], 
        reload=True
    )