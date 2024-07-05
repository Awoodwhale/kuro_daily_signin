import argparse
import datetime
import json
import time

from loguru import logger

from api import (
    bbs_signin,
    get_bbs_forum,
    get_total_gold,
    getpostdetail,
    likeposts,
    mingchao_signin,
    send_dingding_msg,
    shareposts,
)
from login import login

logger.add("kuro.log", level="INFO")


def prepare_login(config_file_path: str, need_write_config: bool):
    phone_number = input("Enter your phone number to get captcha: ")
    assert phone_number != "" and len(phone_number) == 11
    login(
        phone_number,
        need_write_config,
        config_file_path,
    )


def daily_sign(config_file_path: str, need_send_msg: bool = False):
    with open(config_file_path, "r", encoding="u8") as f:
        data = json.load(f)

    dingding_key = data.get("dingdingKey", None)
    dingding_access_token = data.get("dingdingAccessToken", None)
    if not (dingding_access_token and dingding_access_token):
        need_send_msg = False

    users = data.get("users", None)
    assert users is not None

    for i, user in enumerate(users):
        now = datetime.datetime.now()
        month = now.strftime("%m")
        send_msg = ""
        name = user["name"]
        roleId = user["roleId"]
        tokenraw = user["tokenraw"]
        userId = user["userId"]
        devcode = user["devCode"]

        data = {
            "gameId": "3",
            "serverId": "76402e5b20be2c39f095a152090afddc",
            "roleId": roleId,
            "userId": userId,
        }

        # 鸣潮签到
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        msg = f"{current_time} {name} 签到开始"
        send_msg += f"{msg}\n\n"
        logger.info(msg)
        logger.info("=====================================")

        response0 = mingchao_signin(tokenraw, roleId, userId, month)
        if "请求失败" in response0:
            logger.error(response0)
            if i != len(users) - 1:
                logger.info("=====================================")
                logger.info("开始下一个用户签到")
                logger.info("=====================================")
            continue
        if response0:
            msg = f"今天的奖励为：{response0}"
        else:
            msg = "签到失败或没有奖励"

        logger.info(msg)
        send_msg += f"{msg}\n\n"

        logger.info("=====================================")
        time.sleep(1)

        # 库街区签到
        response1 = bbs_signin(tokenraw)
        send_msg += f"{response1}\n\n"
        logger.info(response1)
        logger.info("=====================================")
        msg = "签到完毕，开始点赞帖子"
        logger.info(msg)
        send_msg += f"{msg}\n\n"
        time.sleep(1)

        idlist = get_bbs_forum(tokenraw, devcode)
        post_user_pairs = [
            (post["postId"], post["userId"]) for post in idlist["data"]["postList"]
        ]
        for i, item in enumerate(post_user_pairs):
            postid, userid = item
            getpostdetail(tokenraw, devcode, postid)
            time.sleep(5)
            msg = f"第{i+1}个帖子: {likeposts(tokenraw, devcode, postid, userid)}"
            logger.info(msg)
            send_msg += f"{msg}\n\n"
            if i > 4:
                break
        logger.info("=====================================")

        # 转发帖子
        msg = "点赞完毕，开始转发帖子"
        logger.info(msg)
        send_msg += f"{msg}\n\n"
        msg = shareposts(tokenraw, devcode)
        logger.info(msg)
        send_msg += f"{msg}\n\n"
        logger.info("=====================================")

        # 获取金币数量
        gold = get_total_gold(tokenraw, devcode)
        goldnum = gold["data"]["goldNum"]
        msg = f"金币数量: {goldnum}"
        logger.info(msg)
        send_msg += f"{msg}\n\n"

        now = datetime.datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        msg = f"{current_time} {name} 签到完毕"
        logger.info(msg)
        send_msg += msg

        # 发送钉钉
        if need_send_msg:
            send_dingding_msg(send_msg, dingding_key, dingding_access_token)


def main():
    parser = argparse.ArgumentParser(description="库街区 && 鸣潮自动签到")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        metavar="config file path",
        default="config.json",
        help="配置文件路径",
    )
    parser.add_argument(
        "-s",
        "--send",
        type=bool,
        metavar="send signin result",
        default=True,
        help="是否发送签到结果",
    )
    parser.add_argument(
        "-t",
        "--token",
        action="store_true",
        help="仅将手机号登陆获取的token写入配置文件",
    )
    parser.add_argument(
        "-l",
        "--login",
        action="store_true",
        help="将手机号登陆获取的token写入配置文件后进行签到",
    )

    args = parser.parse_args()

    try:
        if args.token or args.login:
            prepare_login(args.config, True)
            if args.token:
                return
        daily_sign(args.config, args.send)
    except Exception as e:
        logger.error(f"{e}")


if __name__ == "__main__":
    main()
