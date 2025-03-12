import json
import time

import requests

from utils.xianyu_utils import generate_sign, trans_cookies, generate_device_id


class XianyuApis:
    def __init__(self):
        self.url = 'https://h5api.m.goofish.com/h5/mtop.taobao.idlemessage.pc.login.token/1.0/'

    def get_token(self, cookies, device_id):
        headers = {
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'origin': 'https://www.goofish.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.goofish.com/',
            'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
        }
        params = {
            'jsv': '2.7.2',
            'appKey': '34839810',
            't': str(int(time.time()) * 1000),
            'sign': '',
            'v': '1.0',
            'type': 'originaljson',
            'accountSite': 'xianyu',
            'dataType': 'json',
            'timeout': '20000',
            'api': 'mtop.taobao.idlemessage.pc.login.token',
            'sessionOption': 'AutoLoginOnly',
            'spm_cnt': 'a21ybx.im.0.0',
        }
        data_val = '{"appKey":"444e9908a51d1cb236a27862abc769c9","deviceId":"' + device_id + '"}'
        data = {
            'data': data_val,
        }
        token = cookies['_m_h5_tk'].split('_')[0]
        sign = generate_sign(params['t'], token, data_val)
        params['sign'] = sign
        response = requests.post('https://h5api.m.goofish.com/h5/mtop.taobao.idlemessage.pc.login.token/1.0/', params=params, cookies=cookies, headers=headers, data=data)
        res_json = response.json()
        return res_json


if __name__ == '__main__':
    cookies_str = r'_m_h5_tk=cd69ceb8b218792aaa87a25520ac2e42_1741675519283; _m_h5_tk_enc=14e354562a76f1580e9811fe625f0bab; cna=aKpWII3TuhYCAXAC/B2h9RUU; xlly_s=1; cookie2=1c0007f338e2862f1d86acf2dbe0caee; _samesite_flag_=true; t=12eea791e544f5c869c344cd560c13d5; _tb_token_=ee693beb85195; sgcookie=E100itRoJIHwy5c90Opr%2Bzk5oJkLxZgpOVEbETcunZCgLvCu7JOgHOgFYiDNkzSbKhX5et6X%2ForKDW03ETfrqcJ5uCoUK7Fsj5pJTY7bsYO1Obk%3D; tracknick=tb093613712; csg=607ab10a; unb=3888777108; havana_lgc2_77=eyJoaWQiOjM4ODg3NzcxMDgsInNnIjoiMjkwOTY1ZjkxZTVlN2ZkZTQyMTE0MDM4NGJjOWFiZDAiLCJzaXRlIjo3NywidG9rZW4iOiIxeWw4LUcwa0l0YWZxT0hCYy1iZ3ZxQSJ9; _hvn_lgc_=77; havana_lgc_exp=1744259448511; sdkSilent=1741753851109; tfstk=gaLstw0YMR26X92HsAhFOAWD4-7X1KgzlS1vZIUaMNQTH-dRLdWN7j0fHdXe7ORNW5xHUQUw7cb4lNbckYkrz45wsZbYtgKQLOAptshF6OhjVPQckYkUYrIiPZvlKvB2XBhCgs5T6KUA9yBha1QABieLv_BdHZpAXkCdZ_XYXZCTJX1cptQAkKQKaVyCgc1v1fL0kmqtSTAOdrUvJqj1FCE4krLC1GTy69OeTe11fTI33BIJWpRv7Fjnxk7DT39XDLHUbOK5NpsyfYa6FdfvdN8-icjhDETftHDbcTtv_3xAAf39ON61DeJLakb6DdYfjhNmZBQ9K3XlXDDhOF8PcTjQpAdeOOIWcdk3kO-W9psy8JzPy3vBlgQR4_UPFcETcWsul66rOXZ0mLAjYEp21ND5X6ftzXGQdojOt66rOXZ0mGCh63lIOJZc.'
    xianyu = XianyuApis()
