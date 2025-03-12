import base64
import json
import asyncio
from loguru import logger
import websockets
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

    async def send_ack(self, ws, Packet_sid):
        pass

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
        msg = {"lwp":"/r/Conversation/listNewestPagination","headers":{"mid":"8971741704675924 0"},"body":[9007199254740991,50]}
        await ws.send(json.dumps(msg))
        msg = {"lwp":"/r/SingleChatConversation/create","headers":{"mid":"3831741704675925 0"},"body":[{"pairFirst":"3888777108@goofish","pairSecond":"2202640918079@goofish","bizType":"1","extension":{"itemId":"897742748011"},"ctx":{"appVersion":"1.0","platform":"web"}}]}
        await ws.send(json.dumps(msg))
        msg = {"lwp":"/r/SyncStatus/getState","headers":{"mid":"5541741704675930 0"},"body":[{"topic":"sync"}]}
        await ws.send(json.dumps(msg))
        msg = {"lwp":"/r/SyncStatus/ackDiff","headers":{"mid":"5701741704675979 0"},"body":[{"pipeline":"sync","tooLong2Tag":"PNM,1","channel":"sync","topic":"sync","highPts":0,"pts":1741704666107000,"seq":0,"timestamp":1741704675971}]}
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

    async def main(self, toid, item_id, text):
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
            # await self.init(websocket)

            asyncio.create_task(self.init(websocket))
            async for message in websocket:
                try:
                    # logger.info(f"message: {message}")
                    message = json.loads(message)
                    ack = {
                        "code": 200,
                        "headers": {
                            "mid": message["headers"]["mid"],
                            "sid": message["headers"]["sid"]
                        }
                    }
                    if 'app-key' in message["headers"]:
                        ack["headers"]["app-key"] = message["headers"]["app-key"]
                    if 'ua' in message["headers"]:
                        ack["headers"]["ua"] = message["headers"]["ua"]
                    if 'dt' in message["headers"]:
                        ack["headers"]["dt"] = message["headers"]["dt"]
                    await websocket.send(json.dumps(ack))

                    data = message["body"]["syncPushPackage"]["data"][0]["data"]
                    data = decrypt(data)
                    message = json.loads(data)
                    logger.info(f"message: {message}")


                    send_user_name = message["1"]["10"]["reminderTitle"]
                    send_user_id = message["1"]["10"]["senderUserId"]
                    send_message = message["1"]["10"]["reminderContent"]
                    logger.info(f"user: {send_user_name}, 发送给我的信息 message: {send_message}")
                    # reply = f'Hello, {send_user_name}! I am a robot. I am not available now. I will reply to you later.'
                    reply = f'{send_user_name} 说了: {send_message}'
                    cid = message["1"]["2"]
                    cid = cid.split('@')[0]
                    await self.send_msg(websocket, cid, send_user_id, reply)
                except Exception as e:
                    logger.error(e)


if __name__ == '__main__':
    cookies_str = r'cna=aKpWII3TuhYCAXAC/B2h9RUU; xlly_s=1; t=12eea791e544f5c869c344cd560c13d5; tracknick=tb093613712; unb=3888777108; havana_lgc2_77=eyJoaWQiOjM4ODg3NzcxMDgsInNnIjoiMjkwOTY1ZjkxZTVlN2ZkZTQyMTE0MDM4NGJjOWFiZDAiLCJzaXRlIjo3NywidG9rZW4iOiIxeWw4LUcwa0l0YWZxT0hCYy1iZ3ZxQSJ9; _hvn_lgc_=77; havana_lgc_exp=1744259448511; mtop_partitioned_detect=1; _m_h5_tk=ca8b4dd100957488d45be53e94dc572f_1741713249137; _m_h5_tk_enc=f33ec6baacf86eac88d07ffe868e3e57; _samesite_flag_=true; sgcookie=E100lZr6TdR%2F%2BM8eOe%2FYNfKSzRbSpMCf4UIc3o1d%2F7W8mC4HM1DrJ%2F5OtlUg0oBOx00QqwiqNvs72HeWdtbEsXHkRezIHmW30%2BxeGtEBSUKRDa0%3D; cookie2=20517583879846b885456691e45502f4; csg=acfb6894; _tb_token_=f470345e5eb07; sdkSilent=1741791058895; tfstk=gN_mTANz4i-fIy6KHT8bvybQxIE-ljT6DO39BFpa4LJSHx3A_AXGU9CxkNCwIOXJFsKAS1gM_1W_GdFb2s1X5FyLpd4dGs_C_o4beFPNaFdGStWSSs1X5bG-QkIPGAm1ffXw7O8y4CAw7IRNQLRyFCOZ3Cu4Z_JWUqJw3F8yaCdq7cWw77fyFC8wgbPt0pQNYayz4Akd0eTdrIxDLsqI7VboJnvFgL0aBaA0Rp52EVuwHXehz_fYn21JlwBH9tUro9fNOG-lSYyHCafPuG5SnRR5btLyHerqZEQfgM-N8RiNKEXMYZ-o_25fgLTkawPtALQkHO7D4W3HXU7pYES8V-K9oBXNltci795R9Zt5SJDyCidBzCb_TcvMbg8Z4DRlNVOz6aosfnRWZpdKjsgqRprhT7Vov1t2NB9LZ7msfnRWZpFuZDQ60QOBp'

    xianyuLive = XianyuLive(cookies_str)


    # 主动发送一次消息
    to_id = '2202640918079'
    item_id = '897742748011'
    # asyncio.run(xianyuLive.send_msg_once(to_id, item_id, 'Hello, World!'))

    # 常驻进程
    asyncio.run(xianyuLive.main(to_id, item_id, 'Hello, World!'))
