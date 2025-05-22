from fastapi import FastAPI, BackgroundTasks
import threading
import asyncio
from typing import Dict, Optional
from pydantic import BaseModel
import uvicorn
from XianyuAutoAsync import XianyuLive
import ctypes

app = FastAPI()

# 存储活跃会话
active_sessions: Dict[str, threading.Thread] = {}

class CookiesRequest(BaseModel):
    cookies_str: str
    

def run_xianyu_live(cookies_str: str):
    """在单独的线程中运行XianyuLive的main方法"""
    xianyu_live = XianyuLive(cookies_str)
    asyncio.run(xianyu_live.main())

@app.post("/start_session")
async def start_session(request: CookiesRequest, background_tasks: BackgroundTasks):
    """启动新的闲鱼会话，在后台线程中运行
    
    参数:
        request: 包含cookies_str的请求体
        background_tasks: FastAPI的后台任务管理器
    
    返回:
        会话状态信息和会话ID
    """
    # 检查是否已存在使用相同cookies的会话
    session_id = hash(request.cookies_str)
    
    if session_id in active_sessions and active_sessions[session_id].is_alive():
        return {"status": "error", "message": "该cookies已有运行中的会话"}
    
    # 为此会话启动新线程
    thread = threading.Thread(
        target=run_xianyu_live,
        args=(request.cookies_str,),
        daemon=True  # 设置为守护线程，主程序退出时会自动结束
    )
    thread.start()
    
    # 存储线程
    active_sessions[session_id] = thread
    
    return {"status": "success", "message": "会话已启动", "session_id": session_id}

@app.post("/stop_session/{session_id}")
async def stop_session(session_id: int):
    """停止活跃的闲鱼会话
    
    参数:
        session_id: 会话ID
    
    返回:
        操作状态信息
    """
    if session_id not in active_sessions:
        return {"status": "error", "message": "未找到指定会话"}
    
    # 获取线程
    thread = active_sessions[session_id]
    
    # 强制终止线程
    if thread.is_alive():
        thread_id = thread.ident
        if thread_id:
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_long(thread_id),
                ctypes.py_object(SystemExit)
            )
            if res > 1:
                # 如果返回值大于1，说明可能影响了多个线程，需要重置
                ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), None)
                return {"status": "error", "message": "终止线程失败，可能影响了多个线程"}
    
    # 从活跃会话中移除
    active_sessions.pop(session_id)
    return {"status": "success", "message": "会话已终止"}

@app.get("/sessions")
async def list_sessions():
    """列出所有活跃会话
    
    返回:
        活跃会话列表
    """
    return {
        "active_sessions": [
            {"session_id": session_id, "active": thread.is_alive()}
            for session_id, thread in active_sessions.items()
        ]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)  # 启动FastAPI应用，监听所有网络接口的8000端口 