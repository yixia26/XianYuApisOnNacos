import json
import subprocess
from functools import partial
subprocess.Popen = partial(subprocess.Popen, encoding="utf-8")
import execjs

try:
    xianyu_js = execjs.compile(open(r'../static/xianyu_js.js', 'r', encoding='utf-8').read())
except:
    xianyu_js = execjs.compile(open(r'static/xianyu_js.js', 'r', encoding='utf-8').read())

def trans_cookies(cookies_str):
    cookies = dict()
    for i in cookies_str.split("; "):
        try:
            cookies[i.split('=')[0]] = '='.join(i.split('=')[1:])
        except:
            continue
    return cookies


def generate_mid():
    mid = xianyu_js.call('generate_mid')
    return mid

def generate_uuid():
    uuid = xianyu_js.call('generate_uuid')
    return uuid

def generate_device_id(user_id):
    device_id = xianyu_js.call('generate_device_id', user_id)
    return device_id

def generate_sign(t, token, data):
    sign = xianyu_js.call('generate_sign', t, token, data)
    return sign

def decrypt(data):
    res = xianyu_js.call('decrypt', data)
    return res

if __name__ == '__main__':
    # t = 1741667630548
    # token = 'b7e897bf9767618a32b439c6103fe1cb'
    # data = '{"appKey":"444e9908a51d1cb236a27862abc769c9","deviceId":"ED4CBA2C-5DA0-4154-A902-BF5CB52409E2-3888777108"}'
    # print(generate_sign(t, token, data))
    msg = "ggGLAYEBtTIyMDI2NDA5MTgwNzlAZ29vZmlzaAKzNDc4MTI4NzAwMDBAZ29vZmlzaAOxMzQwMzIwNTY4OTU4MS5QTk0EAAXPAAABlYXRFx8GggFlA4UBoAKkMTExMQOgBAEF2gA1eyJhdFVzZXJzIjpbXSwiY29udGVudFR5cGUiOjEsInRleHQiOnsidGV4dCI6IjExMTEifX0HAggBCQAKi6lfcGxhdGZvcm2nYW5kcm9pZKZiaXpUYWfaAEF7InNvdXJjZUlkIjoiUzoxIiwibWVzc2FnZUlkIjoiNmQzYTI0YzBkNTNmNGQzMmJjNjExMGYzMzFjNWI5YTAifaxkZXRhaWxOb3RpY2WkMTExMadleHRKc29u2gBLeyJxdWlja1JlcGx5IjoiMSIsIm1lc3NhZ2VJZCI6IjZkM2EyNGMwZDUzZjRkMzJiYzYxMTBmMzMxYzViOWEwIiwidGFnIjoidSJ9r3JlbWluZGVyQ29udGVudKQxMTExrnJlbWluZGVyTm90aWNlteWPkeadpeS4gOadoeaWsOa2iOaBr61yZW1pbmRlclRpdGxlpnNoYeS/rqtyZW1pbmRlclVybNoAm2ZsZWFtYXJrZXQ6Ly9tZXNzYWdlX2NoYXQ/aXRlbUlkPTg5Nzc0Mjc0ODAxMSZwZWVyVXNlcklkPTIyMDI2NDA5MTgwNzkmcGVlclVzZXJOaWNrPXQqKioxJnNpZD00NzgxMjg3MDAwMCZtZXNzYWdlSWQ9NmQzYTI0YzBkNTNmNGQzMmJjNjExMGYzMzFjNWI5YTAmYWR2PW5vrHNlbmRlclVzZXJJZK0yMjAyNjQwOTE4MDc5rnNlbmRlclVzZXJUeXBloTCrc2Vzc2lvblR5cGWhMQwBA4GobmVlZFB1c2ikdHJ1ZQ==";
    res = decrypt(msg)
    print(res)