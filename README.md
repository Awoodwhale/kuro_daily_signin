# kuro_daily_signin

库街区论坛每日签到 && 鸣潮每日签到

## 环境依赖

- NodeJS
  - 国内:<https://nodejs.cn/download/>
  - 官网:[Node.js — Download Node.js® (nodejs.org)](https://nodejs.org/en/download/package-manager)
  - 本项目开发时使用`v22.3.0`
- Python环境
  - 使用`Python3.8`及以上（项目开发时使用`Python3.12.4`）
  - 建议使用`venv`创建本项目的环境, `python3 -m venv ./venv`
  - 在venv中安装本项目的依赖库 `pip3 install -r requirements.txt`

## 脚本参数

```bash
usage: main.py [-h] [-c config file path] [-s send signin result] [-t] [-l]

库街区 && 鸣潮自动签到

options:
  -h, --help            show this help message and exit
  -c config file path, --config config file path
                        配置文件路径
  -s send signin result, --send send signin result
                        是否发送签到结果
  -t, --token           仅将手机号登陆获取的token写入配置文件
  -l, --login           将手机号登陆获取的token写入配置文件后进行签到
```

## 相关项目

[mxyooR/Kuro-autosignin](https://github.com/mxyooR/Kuro-autosignin)