# !/usr/bin/python3.5
# -*- coding: utf-8 -*-
"""
@ProjectDistribution:
@Time: 2018/11/16 21:23
@Author: Marus
@Function:handlers.py.py
"""

# !/usr/bin/python3.5
# -*- coding: utf-8 -*-
"""
@ProjectDistribution:
@Time: 2018/10/30 19:59
@Author: Marus
@Function:handlers.py
"""

' url handlers '

import re, time, json, logging, hashlib, base64, asyncio, xmltodict
from coroweb import get, post
from models_version_1 import User, ClickEvent, SubscribeEvent, MenuEvent, Message, ViewEvent, Server_wx, Order_wx
from flask import Flask
app = Flask(__name__, static_url_path='')
from PASS_secret import appname_lx, appid_lx, appsecret_lx, token_lx,\
    appname_aijiu, appid_aijiu, appsecret_aijiu, token_aijiu\

# server & order
sw = Server_wx(
        appid=appid_lx,
        appname='lexiang',
        appsecret=appsecret_lx,
        apptoken=token_lx,
        appencodingasekey=None
    )
ow = Order_wx(
        appid=appid_aijiu,
        appname='aijiu',
        appsecret=appsecret_aijiu,
        apptoken=token_aijiu,
        appencodingasekey=None
    )

@app.route('/', methods=['POST'])
def handle_post():
    timestamp = request.args.get('timestamp')
    nonce = request.args.get('nonce')
    signature = request.args.get('signature')
    if ow.token_verify(timestam=timestamp, nonce=nonce, signature=signature):
        resp_dict = xmltodict.parse(request.data).get('xml')
        event = resp_dict.get('Event')
        eventkey = resp_dict.get('EventKey')
        touserName = resp_dict.get('ToUserName')
        fromuserName = resp_dict.get('FromUserName')
        if event == 'CLICK' and eventkey == 'v10014_qrcode':
            MenuEvent(menu_id='10014', menu_name=eventkey, menu_event=event, click_num=1, update_time=timestamp,
                      create_time=timestamp)
            # 请求获取到unionId
            result = ow.get_member_info(fromuserName)
            print(result)
            app.logger.info(str(result))
            unionId = result['unionid']
            img_path = sw.return_comcat_img(state=unionId)
            result_xml = ow.answer_picture(unionId=unionId, touserName=touserName, img_path=img_path)
            return result_xml
        elif event == 'CLICK' and eventkey == 'v10015_recommendation':
            MenuEvent(menu_id='10015', menu_name=eventkey, menu_event=event, click_num=1, update_time=timestamp,
                      create_time=timestamp)
            result = ow.get_member_info(fromuserName)
            unionId = result['unionid']



@app.get('/', methods=['GET'])
def handle_get():
    pass