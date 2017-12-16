#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AliPayConfig(object):
    # 商户app_id
    app_id = "2016081500252288"
    # app_id = "2016082500309412"



    # 商户私钥路径
    merchant_private_key_path = os.path.join(BASE_DIR, "keys", "app_private_2048.txt")
    # merchant_private_key_path = os.path.join(BASE_DIR, "keys", "pri")

    # 支付宝公钥路径
    alipay_public_key_path = os.path.join(BASE_DIR, "keys", "alipay_public_2048.txt")
    # alipay_public_key_path = os.path.join(BASE_DIR, "keys", "pub")

    # 服务器异步通知页面路径 需http: // 格式的完整路径，不能加?id = 123 这类自定义参数，必须外网可以正常访问
    # 发post请求
    notify_url = "http://47.94.172.250:8804/api/v1/trade/alipay/"

    # 页面跳转同步通知页面路径 需http: // 格式的完整路径，不能加?id = 123 这类自定义参数，必须外网可以正常访问
    # 发get请求
    return_url = "http://47.94.172.250:8804/api/v1/trade/alipay/"

    # 签名方式(当前只支持RSA和RSA2)
    sign_type = "RSA2"

    # 字符编码格式
    charset = "utf-8"

    # 支付宝网关(如果是线上环境的话, dev 这三个字去掉即可)
    gateway_url = "https://openapi.alipaydev.com/gateway.do"

    # 异步通知参数DOC(支付宝会主动发起POST请求)
    notify_doc = "https://docs.open.alipay.com/270/105902/"
