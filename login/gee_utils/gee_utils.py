import json
import os
import urllib.parse

import ddddocr
import execjs
import requests
from loguru import logger

from . import track_utils

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
}

current_dir = os.path.dirname(os.path.abspath(__file__))
gee_js_path = os.path.join(current_dir, "geeTest.js")
with open(gee_js_path, "r") as f:
    gee_test_text = f.read()


def __convert_call_back(callBackSign: str, context: str):
    return json.loads(context[len(callBackSign) + 1 : len(context) - 1])


def gee_load(call_back_sign: str, captcha_id: str):
    url = "https://gcaptcha4.geetest.com/load"
    params = {
        "callback": call_back_sign,
        "captcha_id": captcha_id,
        "client_type": "web",
        "pt": "1",
        "lang": "zho",
    }
    response = requests.get(url, headers=headers, params=params)
    return __convert_call_back(callBackSign=call_back_sign, context=response.text)


def gee_slide_analyse(bg_path: str, slice_path: str):
    # Get the geetest picture
    geeHost = "https://static.geetest.com/"
    targetUrl = urllib.parse.urljoin(geeHost, slice_path)
    bgUrl = urllib.parse.urljoin(geeHost, bg_path)
    targetBytes = requests.get(url=targetUrl, headers=headers).content
    bgBytes = requests.get(url=bgUrl, headers=headers).content

    # Identify
    det = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
    target = det.slide_match(
        target_bytes=targetBytes, background_bytes=bgBytes, simple_target=True
    )["target"]
    distance = target[0]
    logger.debug(f"Get target ==> {target}")
    sliceTime = track_utils.get_slide_track_time(distance=distance)
    return {"distance": distance, "time": sliceTime}


def gee_sec_code(call_back_sign: str, captcha_id: str):
    gee_load_data = gee_load(call_back_sign, captcha_id)["data"]
    geeDetectInfo = gee_slide_analyse(
        bg_path=gee_load_data["bg"], slice_path=gee_load_data["slice"]
    )
    logger.debug(f"Detect GeeTest Slice ==> {geeDetectInfo}")
    lot_number = gee_load_data["lot_number"]
    w = execjs.compile(gee_test_text).call(
        "geeTestW",
        geeDetectInfo["distance"],
        geeDetectInfo["time"],
        lot_number,
        gee_load_data["pow_detail"]["datetime"],
        captcha_id,
    )
    logger.debug(f"Get W ==> {w}")
    url = "https://gcaptcha4.geetest.com/verify"
    params = {
        "callback": call_back_sign,
        "captcha_id": captcha_id,
        "client_type": "web",
        "lot_number": lot_number,
        "payload": gee_load_data["payload"],
        "process_token": gee_load_data["process_token"],
        "payload_protocol": "1",
        "pt": "1",
        "w": w,
    }
    response = requests.get(url=url, params=params, headers=headers)
    responseJson = __convert_call_back(
        callBackSign=call_back_sign, context=response.text
    )
    result = responseJson["data"]["result"]
    if result != "success":
        logger.error("滑块请求失败,请重新尝试")
        return None
    return json.dumps(
        __convert_call_back(callBackSign=call_back_sign, context=response.text)["data"][
            "seccode"
        ]
    )
