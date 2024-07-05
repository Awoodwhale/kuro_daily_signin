import json
import os
import time

import requests
from loguru import logger

from .gee_utils import gee_utils


def get_current_stamp_ms():
    return round(time.time() * 1000)


# send SMS Code
def send_sms_code(phone_number: str, device_code: str, captcha_id: str):
    headers = {
        "Host": "api.kurobbs.com",
        "osversion": "Android",
        "devcode": device_code,
        "countrycode": "CN",
        "model": "MIX 2",
        "source": "android",
        "lang": "zh-Hans",
        "version": "2.2.0",
        "versioncode": "2200",
        "channelid": "4",
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "okhttp/3.11.0",
    }
    call_back_sign = f"geetest_{get_current_stamp_ms()}"
    seccode = gee_utils.gee_sec_code(
        call_back_sign=call_back_sign, captcha_id=captcha_id
    )
    logger.debug(f"Get seccode ==> {seccode}")
    url = "https://api.kurobbs.com/user/getSmsCode"
    data = {"mobile": phone_number, "geeTestData": seccode}
    response = requests.post(url, headers=headers, data=data)
    return response.json()


# Step 3: Perform login with the SMS code
def sdk_login(phone_number: str, sms_code: str, device_code: str):
    headers = {
        "Host": "api.kurobbs.com",
        "osversion": "Android",
        "devcode": device_code,
        "countrycode": "CN",
        "model": "MIX 2",
        "source": "android",
        "lang": "zh-Hans",
        "version": "2.2.0",
        "versioncode": "2200",
        "channelid": "4",
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "okhttp/3.11.0",
    }
    url = "https://api.kurobbs.com/user/sdkLogin"
    data = {
        "code": sms_code,
        "devCode": device_code,
        "gameList": "",
        "mobile": phone_number,
    }
    response = requests.post(url=url, data=data, headers=headers)
    json_res = response.json()
    if json_res["code"] != 200:
        logger.error(json_res["msg"])
        return False
    return json_res["data"]


def get_data(token: str, device_code: str, refresh: bool = False):
    headers = {
        "Host": "api.kurobbs.com",
        "devcode": device_code,
        "source": "android",
        "version": "2.2.0",
        "versioncode": "2200",
        "token": token,
        "osversion": "Android",
        "countrycode": "CN",
        "model": "MIX 2",
        "lang": "zh-Hans",
        "channelid": "4",
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "okhttp/3.11.0",
    }
    cookies = {"user_token": token}
    if refresh:
        url = "https://api.kurobbs.com/gamer/widget/game3/refresh"
    else:
        url = "https://api.kurobbs.com/gamer/widget/game3/getData"
    data = {"type": "1", "sizeType": "2"}
    response = requests.post(url, headers=headers, cookies=cookies, data=data)
    json_res = response.json()
    if json_res["code"] != 200:
        return logger.error(json_res["msg"])
    return json_res["data"]


def login(
    phone_number: str | int = "",
    need_write_json: bool = True,
    json_file_path: str = "config.json",
):
    # Geetest Id of wuthering waves (android)
    captcha_id = "3f7e2d848ce0cb7e7d019d621e556ce2"
    deviceId = "9DE7B0405471B76E018AA599A3A7D9676DCB9D66"
    phone_number = str(phone_number)
    if not phone_number:
        phone_number = input("Enter your phone number: ")
    status = send_sms_code(
        phone_number=phone_number, device_code=deviceId, captcha_id=captcha_id
    )
    logger.debug(status["msg"])
    sms_code = input("Enter the SMS code: ")
    login_resp = sdk_login(
        phone_number=phone_number, sms_code=sms_code, device_code=deviceId
    )
    logger.debug(f"Login Response ==> \n{login_resp}")
    token = login_resp["token"] or ""
    userId = login_resp["userId"]
    dataResponse = get_data(token=token, device_code=deviceId)
    meta = {
        "token": token,
        "userId": userId,
        "roleId": dataResponse["roleId"],
        "roleName": dataResponse["roleName"],
        "serverId": dataResponse["serverId"],
    }
    logger.info(f"Get login Info ==> \n{meta}")

    if token and need_write_json and json_file_path:
        data: dict = {"dingdingKey": "", "dingdingAccessToken": "", "users": []}
        if os.path.exists(json_file_path):
            try:
                with open(json_file_path, "r", encoding="u8") as f:
                    data = json.load(f)
            except Exception:
                pass

        data["users"].append(
            {
                "name": meta["roleName"],
                "roleId": meta["roleId"],
                "tokenraw": meta["token"],
                "userId": meta["userId"],
                "devCode": "127.0.0.1, Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) KuroGameBox/2.2.0",
            }
        )
        with open(json_file_path, "w", encoding="u8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
