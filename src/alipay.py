#! /usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from urllib.parse import quote_plus
from urllib.parse import urlparse, parse_qs
from base64 import decodebytes, encodebytes

from config.settings import AliPayConfig

import json


# 文档链接(支付成功回调通知参数等相关, 支付宝交易状态是 TRADE_SUCCESS 会主动发起异步通知)
# https://docs.open.alipay.com/270/105902/

# 沙箱测试环境可使用沙箱支付宝支付
# 账号: rjoegs7144@sandbox.com
# 密码: 111111
# 支付密码: 111111


class AliPay(object):
    """
    支付宝支付接口(PC端支付接口)
    """

    def __init__(self, appid, app_notify_url, app_private_key_path,
                 alipay_public_key_path, return_url, debug=False):
        self.appid = appid
        self.app_notify_url = app_notify_url
        self.app_private_key_path = app_private_key_path
        self.app_private_key = None
        self.return_url = return_url
        with open(self.app_private_key_path) as fp:
            self.app_private_key = RSA.importKey(fp.read())
        self.alipay_public_key_path = alipay_public_key_path
        with open(self.alipay_public_key_path) as fp:
            self.alipay_public_key = RSA.importKey(fp.read())

        if debug is True:
            self.__gateway = "https://openapi.alipaydev.com/gateway.do"
        else:
            self.__gateway = "https://openapi.alipay.com/gateway.do"

    def direct_pay(self, subject, out_trade_no, total_amount, return_url=None, **kwargs):
        biz_content = {
            "subject": subject,
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "product_code": "FAST_INSTANT_TRADE_PAY",
            # "qr_pay_mode":4
        }

        biz_content.update(kwargs)
        data = self.build_body("alipay.trade.page.pay", biz_content, self.return_url)
        return self.sign_data(data)

    def build_body(self, method, biz_content, return_url=None):
        data = {
            "app_id": self.appid,
            "method": method,
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }

        if return_url is not None:
            data["notify_url"] = self.app_notify_url
            data["return_url"] = self.return_url

        return data

    def sign_data(self, data):
        data.pop("sign", None)
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        unsigned_string = "&".join("{0}={1}".format(k, v) for k, v in unsigned_items)
        sign = self.sign(unsigned_string.encode("utf-8"))
        # ordered_items = self.ordered_data(data)
        quoted_string = "&".join("{0}={1}".format(k, quote_plus(v)) for k, v in unsigned_items)

        # 获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string

    def ordered_data(self, data):
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)

        # 将字典类型的数据dump出来
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))

        return sorted([(k, v) for k, v in data.items()])

    def sign(self, unsigned_string):
        # 开始计算签名
        key = self.app_private_key
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(SHA256.new(unsigned_string))
        # base64 编码，转换为unicode表示并移除回车
        sign = encodebytes(signature).decode("utf8").replace("\n", "")
        return sign

    def _verify(self, raw_content, signature):
        # 开始计算签名
        key = self.alipay_public_key
        signer = PKCS1_v1_5.new(key)
        digest = SHA256.new()
        digest.update(raw_content.encode("utf8"))
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):
            return True
        return False

    def verify(self, data, signature):
        if "sign_type" in data:
            sign_type = data.pop("sign_type")
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)
        return self._verify(message, signature)


if __name__ == "__main__":
    # 这一部分是验证url的签名
    return_url = 'http://47.92.87.172:8000/?total_amount=100.00&timestamp=2017-08-15+23%3A53%3A34&sign=e9E9UE0AxR84NK8TP1CicX6aZL8VQj68ylugWGHnM79zA7BKTIuxxkf%2FvhdDYz4XOLzNf9pTJxTDt8tTAAx%2FfUAJln4WAeZbacf1Gp4IzodcqU%2FsIc4z93xlfIZ7OLBoWW0kpKQ8AdOxrWBMXZck%2F1cffy4Ya2dWOYM6Pcdpd94CLNRPlH6kFsMCJCbhqvyJTflxdpVQ9kpH%2B%2Fhpqrqvm678vLwM%2B29LgqsLq0lojFWLe5ZGS1iFBdKiQI6wZiisBff%2BdAKT9Wcao3XeBUGigzUmVyEoVIcWJBH0Q8KTwz6IRC0S74FtfDWTafplUHlL%2Fnf6j%2FQd1y6Wcr2A5Kl6BQ%3D%3D&trade_no=2017081521001004340200204115&sign_type=RSA2&auth_app_id=2016080600180695&charset=utf-8&seller_id=2088102170208070&method=alipay.trade.page.pay.return&app_id=2016080600180695&out_trade_no=20170202185&version=1.0'
    o = urlparse(return_url)
    query = parse_qs(o.query)
    processed_query = {}
    ali_sign = query.pop("sign")[0]

    alipay = AliPay(
        appid=AliPayConfig.app_id,
        app_notify_url=AliPayConfig.notify_url,
        return_url=AliPayConfig.return_url,
        app_private_key_path=AliPayConfig.merchant_private_key_path,
        alipay_public_key_path=AliPayConfig.alipay_public_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥
        debug=True,  # 默认False,
    )

    for key, value in query.items():
        processed_query[key] = value[0]

    # 验证签名校验的结果
    print(alipay.verify(processed_query, ali_sign))

    # 生成支付的url
    query_params = alipay.direct_pay(
        subject="luffycity",  # 商品简单描述
        out_trade_no="asdfasdfa",  # 商户订单号
        total_amount=100.00,  # 交易金额(单位: 元 保留俩位小数)
    )

    pay_url = "https://openapi.alipaydev.com/gateway.do?{}".format(query_params)

    print(pay_url)
