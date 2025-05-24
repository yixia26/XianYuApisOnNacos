import base64
import json
import asyncio
import time

from loguru import logger
import websockets
import redis
from XianyuApis import XianyuApis

from utils.xianyu_utils import generate_mid, generate_uuid, trans_cookies, generate_device_id, decrypt


class XianyuLive:
    def __init__(self, cookies_str):
        self.xianyu = XianyuApis()
        self.base_url = 'wss://wss-goofish.dingtalk.com/'
        self.cookies_str = cookies_str
        self.cookies = trans_cookies(cookies_str)
        self.myid = self.cookies['unb']
        self.device_id = generate_device_id(self.myid)
        self.ws = None
        # 初始化Redis连接
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        # 存储活跃会话ID
        self.active_cids = set()


    async def create_chat(self, ws, toid, item_id='891198795482'):
        msg = {
            "lwp": "/r/SingleChatConversation/create",
            "headers": {
                "mid": generate_mid()
            },
            "body": [
                {
                    "pairFirst": f"{toid}@goofish",
                    "pairSecond": f"{self.myid}@goofish",
                    "bizType": "1",
                    "extension": {
                        "itemId": item_id
                    },
                    "ctx": {
                        "appVersion": "1.0",
                        "platform": "web"
                    }
                }
            ]
        }
        await ws.send(json.dumps(msg))

    async def send_msg(self, ws, cid, toid, text):
        # 47781902407
        # 1130441829
        text = {
            "contentType": 1,
            "text": {
                "text": text
            }
        }
        text_base64 = str(base64.b64encode(json.dumps(text).encode('utf-8')), 'utf-8')
        msg = {
            "lwp": "/r/MessageSend/sendByReceiverScope",
            "headers": {
                "mid": generate_mid()
            },
            "body": [
                {
                    "uuid": generate_uuid(),
                    "cid": f"{cid}@goofish",
                    "conversationType": 1,
                    "content": {
                        "contentType": 101,
                        "custom": {
                            "type": 1,
                            "data": text_base64
                        }
                    },
                    "redPointPolicy": 0,
                    "extension": {
                        "extJson": "{}"
                    },
                    "ctx": {
                        "appVersion": "1.0",
                        "platform": "web"
                    },
                    "mtags": {},
                    "msgReadStatusSetting": 1
                },
                {
                    "actualReceivers": [
                        f"{toid}@goofish",
                        f"{self.myid}@goofish"
                    ]
                }
            ]
        }
        await ws.send(json.dumps(msg))

    async def init(self, ws):
        token = self.xianyu.get_token(self.cookies, self.device_id)['data']['accessToken']
        msg = {
            "lwp": "/reg",
            "headers": {
                "cache-header": "app-key token ua wv",
                "app-key": "444e9908a51d1cb236a27862abc769c9",
                "token": token,
                "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 DingTalk(2.1.5) OS(Windows/10) Browser(Chrome/133.0.0.0) DingWeb/2.1.5 IMPaaS DingWeb/2.1.5",
                "dt": "j",
                "wv": "im:3,au:3,sy:6",
                "sync": "0,0;0;0;",
                "did": self.device_id,
                "mid": generate_mid()
            }
        }
        await ws.send(json.dumps(msg))
        current_time = int(time.time() * 1000)
        msg = {
            "lwp": "/r/SyncStatus/ackDiff",
            "headers": {"mid": generate_mid()},
            "body": [
                {
                    "pipeline": "sync",
                    "tooLong2Tag": "PNM,1",
                    "channel": "sync",
                    "topic": "sync",
                    "highPts": 0,
                    "pts": current_time * 1000,
                    "seq": 0,
                    "timestamp": current_time
                }
            ]
        }
        await ws.send(json.dumps(msg))
        logger.info('init')


    async def send_msg_once(self, toid, item_id, text):
        headers = {
            "Cookie": self.cookies_str,
            "Host": "wss-goofish.dingtalk.com",
            "Connection": "Upgrade",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Origin": "https://www.goofish.com",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        async with websockets.connect(self.base_url, extra_headers=headers) as websocket:
            await self.init(websocket)
            await self.create_chat(websocket, toid, item_id)
            async for message in websocket:
                try:
                    logger.info(f"message: {message}")
                    message = json.loads(message)
                    cid = message["body"]["singleChatConversation"]["cid"]
                    cid = cid.split('@')[0]
                    await self.send_msg(websocket, cid, toid, text)
                    logger.info('send message')
                    return
                except Exception as e:
                    pass

    async def heart_beat(self, ws):
        while True:
            msg = {
                "lwp": "/!",
                "headers": {
                    "mid": generate_mid()
                 }
            }
            await ws.send(json.dumps(msg))
            await asyncio.sleep(15)

    async def store_message_to_redis(self, sender_id, sender_name, message, cid):
        """
        将消息存储到Redis中
        使用msg:{cid}列表存储该会话的所有消息历史
        """
        msg_data = {
            "sender_id": sender_id,
            "sender_name": sender_name,
            "message": message,
            "cid": cid,
            "timestamp": int(time.time())
        }
        # 使用cid作为键，将消息追加到列表中
        msg_key = f"customer:message:{cid}"
        self.redis_client.rpush(msg_key, json.dumps(msg_data, ensure_ascii=False))
        logger.info(f"消息已添加到Redis列表: {msg_key}")

    async def check_pending_messages(self, ws):
        """
        定时检查Redis中待发送的消息并发送
        使用Redis列表(List)存储待发送消息
        只发送当前活跃会话的消息
        """
        while True:
            try:
                # 仅检查当前活跃会话的待发送消息
                for cid in self.active_cids:
                    key = f"ai:pending_msg:{cid}"
                    # 从列表左侧弹出一条待发送消息
                    msg_data_raw = self.redis_client.lpop(key)
                    if msg_data_raw:
                        msg_data = json.loads(msg_data_raw)
                        # 发送消息
                        await self.send_msg(
                            ws, 
                            msg_data["cid"], 
                            msg_data["to_id"], 
                            msg_data["text"]
                        )
                        logger.info(f"已发送定时消息: {msg_data['text']} 到用户 {msg_data['to_id']}, 会话ID: {cid}")
            except Exception as e:
                logger.error(f"处理待发送消息时出错: {e}")
            # 每5秒检查一次
            await asyncio.sleep(5)

    async def main(self):
        headers = {
            "Cookie": self.cookies_str,
            "Host": "wss-goofish.dingtalk.com",
            "Connection": "Upgrade",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Origin": "https://www.goofish.com",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        async with websockets.connect(self.base_url, extra_headers=headers) as websocket:
            asyncio.create_task(self.init(websocket))
            asyncio.create_task(self.heart_beat(websocket))
            # 启动定时检查待发送消息的任务
            asyncio.create_task(self.check_pending_messages(websocket))
            
            async for message in websocket:
                # logger.info(f"message: {message}")
                try:
                    message = json.loads(message)
                    ack = {
                        "code": 200,
                        "headers": {
                            "mid": message["headers"]["mid"] if "mid" in message["headers"] else generate_mid(),
                            "sid": message["headers"]["sid"] if "sid" in message["headers"] else '',
                        }
                    }
                    if 'app-key' in message["headers"]:
                        ack["headers"]["app-key"] = message["headers"]["app-key"]
                    if 'ua' in message["headers"]:
                        ack["headers"]["ua"] = message["headers"]["ua"]
                    if 'dt' in message["headers"]:
                        ack["headers"]["dt"] = message["headers"]["dt"]
                    await websocket.send(json.dumps(ack))
                except Exception as e:
                    pass

                try:
                    data = message["body"]["syncPushPackage"]["data"][0]["data"]
                    logger.info(f"message: {data}")
                    try:
                        data = json.loads(data)
                        logger.info(f"无需解密 message: {data}")
                    except Exception as e:
                        logger.error(f'1 {e}')
                        data = decrypt(data)
                        message = json.loads(data)
                        logger.info(f"message: {message}")

                        send_user_name = message["1"]["10"]["reminderTitle"]
                        send_user_id = message["1"]["10"]["senderUserId"]
                        send_message = message["1"]["10"]["reminderContent"]
                        logger.info(f"user: {send_user_name}, 发送给我的信息 message: {send_message}")
                        
                        # 将接收到的消息存储到Redis
                        cid = message["1"]["2"]
                        cid = cid.split('@')[0]
                        # 将cid添加到活跃会话集合
                        self.active_cids.add(cid)
                        await self.store_message_to_redis(send_user_id, send_user_name, send_message, cid)
                        
                        reply = f'{send_user_name} 说了: {send_message}'
                        await self.send_msg(websocket, cid, send_user_id, reply)
                except Exception as e:
                    logger.error(f'2 {e}')


if __name__ == '__main__':
    cookies_str = r'cna=2bCpIPJCtQICAXH4oggNvfcR; t=ba5ed498d632bb98698a633843877146; isg=BJmZt3q5FS3Z-sm_fs-toEumqINzJo3YhWmXS7tPeEA_wrpUA3b3qMARwYa0-iUQ; xlly_s=1; mtop_partitioned_detect=1; _m_h5_tk=37f62ce4fdfe13071ef15142d4d4b134_1747891514382; _m_h5_tk_enc=d0b3a9ef9e60909b5580e409e584405f; _samesite_flag_=true; cookie2=1b6bdfbeda79019de6c7837763efd98f; _tb_token_=761be633e5837; sdkSilent=1747969996397; tracknick=xy574840311154; unb=2219823870285; sgcookie=E1005m6TvxSKfI8tA1oVenhOxWtLWig1XvKpQua7au7lRDj5pMna4rwc65StVXBxfrNZS5rP6666byvCR8Ja0vchVG0xKLDn%2B%2Fq3eDkLUlxfY8A%3D; csg=6dc73b45; havana_lgc2_77=eyJoaWQiOjIyMTk4MjM4NzAyODUsInNnIjoiOWZlOTEyODM2MjAyYzVhMzIwMTMwMDczMGI1OGQ3YzciLCJzaXRlIjo3NywidG9rZW4iOiIxa2pSWV9CY0FreUdFSGFFd09WZFlyQSJ9; _hvn_lgc_=77; havana_lgc_exp=1750478734845; tfstk=gFTsiItARKLe7gbYGGcFN_JpzGQXfXuzcS1vZIUaMNQTH-dRLdWN7j0fHdXe7ORNWqTfSe-auOkGlIpPlYkrz4RMsN_xUYPSu1mRks3VHDSOsJaOXYkrz2oT9ZMsUKRvJ5MCi9COMOItOJClprU9HOILp_1lkZpAD9FdNsaOHPCO9X1cptQAkKQKOsWdHUD4G6klKCGGaNiA3yXy69aYkFgcfTOb0rUv-1s1sCBBTB8C1G6RDwb4jUOJ6UfXobEfhI-9Q6vjPv_p5dTOAZgb-NRWvdsBfxaCxHdkkMtnFuAk6dtR2F3I1K9pZ3b9Wx4NIndpk98tgr6J4QbCtEk3WttpDFSGoRH1OFOWlnsPnzW57xqbOg4fOTlIOoq0QeIGl5idaXIOt6oZOXZPcGChOZhIOoqcX6fEMXGQ4i1..'

    xianyuLive = XianyuLive(cookies_str)
    # 常驻进程 用于接收消息和自动回复
    asyncio.run(xianyuLive.main())
