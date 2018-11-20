# !/usr/bin/python3.5
# -*- coding: utf-8 -*-
"""
@ProjectDistribution:
@Time: 2018/11/12 19:16
@Author: Marus
@Function:models_version_1.py
"""

import time, uuid
import requests, json
from PIL import Image
import qrcode
from orm_version_1 import Base_wx, Model, StringField, BooleanField, FloatField, TextField, IntegerField, DateTimeField
from datetime import datetime


def next_id():
    return '%015d%000' % (int(time.time() * 1000), uuid.uuid4().hex)

class User(Model):
    __table__ = 'users'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    unionId = StringField(ddl='varchar(80)')
    nickName = StringField(ddl='varchar(50)')
    Sex = StringField(ddl='varchar(20)')
    City = StringField(ddl='varchar(50)')
    Province = StringField(ddl='varchar(50)')
    Country = StringField(ddl='varchar(50)')
    created_at = StringField(ddl='varchar(50)')

class UserRe(Model):
    __table__ = 'user_re'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    referrer = StringField(ddl='varchar(80)')
    referee = StringField(ddl='varchar(80)')
    createTime = StringField(ddl='datetime')

class ClickEvent(Model):
    __table__ = 'clickevent'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    fromuserName = StringField(ddl='varchar(80)')
    clickuserName = StringField(ddl='varchar(80)')
    clickTime = StringField(ddl='datetime')

class SubscribeEvent(Model):
    __table__ = 'subscribe_event'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    event_time = DateTimeField(ddl='datetime')
    event_type = StringField(ddl='varchar(50)')
    send_id = StringField(ddl='varchar(100)')
    union_id = StringField(ddl='varchar(100)')
    create_time = DateTimeField(ddl='datetime')

class MenuEvent(Model):
    __table__ = 'menu_event'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    menu_id = StringField(ddl='varchar(50)')
    menu_name = StringField(ddl='varchar(50)')
    menu_event = StringField(ddl='varchar(50)')
    click_num = IntegerField(ddl='int')
    create_time = DateTimeField(ddl='datetime')

class Message(Model):
    __table__ = 'message'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    send_id = StringField(ddl='varchar(100)')
    union_id = StringField(ddl='varchar(100)')
    message = TextField(ddl='text')
    message_type = StringField(ddl='varchar(50)')
    send_time = DateTimeField(ddl='datetime')

class ViewEvent(Model):
    __table__ = 'view_event'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    send_id = StringField(ddl='varchar(100)')
    from_id = StringField(ddl='varchar(100)')
    union_id = StringField(ddl='varchar(100)')
    view_time = DateTimeField(ddl='datetime')

class Server_wx(Base_wx):
    """
    Server WeChat Public Number
    """
    def __init__(self, name):
        super.__init__(Server_wx)

    def __print_at(self):
        at = self.get_at()
        print(at)
        return at

    def return_at(self):
        at = self.__print_at()
        return at

    def return_qrcode_img(self, state):
        redirect_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?redirect_uri=http%3A%2F%2Fapi.health.92wan.com%2F&scope=snsapi_userinfo&response_type=code&appid={}&state={}#wechat_redirect'.format(
            self.__appId, state)
        qrcode_img = qrcode.make(redirect_url)
        return qrcode_img

    def return_concat_img(self, state, is_concat=1):
        qrcode_img = self.return_qrcode_img(state)
        pic1 = '/home/ubuntu/TestingWebServer-master/flask_webServer/backup/backup.jpg'
        top_img = qrcode_img
        # 缩小图片
        mwidth = 180
        mheight = 180
        top_img_w, top_img_h = top_img.size
        if is_concat == 0:
            return qrcode_img
        if (1.0 * top_img_w / mwidth) > (1.0 * top_img_h / mheight):
            scale = 1.0 * top_img_w / mwidth
            new_im = top_img.resize((int(top_img_w / scale), int(top_img_h / scale)), Image.ANTIALIAS)
        else:
            scale = 1.0 * top_img_h / mheight
            new_im = top_img.resize((int(top_img_w / scale), int(top_img_h / scale)), Image.ANTIALIAS)
        new_im_w, new_im_h = new_im.size
        # load in the bottom image
        bottom_img = Image.open(pic1, 'r')
        # get the size or use 150x150 if it's constant
        bottom_img_w, bottom_img_h = bottom_img.size
        # offset the top image so it's placed in the middle of the bottom image
        offset = ((bottom_img_w - new_im_w) - 436, (bottom_img_h - new_im_h) + 3)
        # embed top_img on top of bottom_img
        bottom_img.paste(new_im, offset)
        img_dir = '/home/ubuntu/TestingWebServer-master/flask_webServer/qrcode_png/'
        img_path = img_dir + state + '.jpg'
        bottom_img.save(img_path)
        return img_path

    def get_member_info_by_code(self, code):
        """
        use the special way by using the return-parameters code
        :param code:
        :return:
        """
        data = {
            'grant_type': 'authorization_code',
            'appid': self.__appId,
            'code': code,
            'secret': self.__appSecret
        }
        url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        resp = requests.get(url, params=data)
        resp_dict = json.loads(resp.text)
        t = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        if 'unionid' in resp_dict:
            unionId = resp_dict['unionid']
        else:
            unionId = ''

        return unionId, t

class Order_wx(Base_wx):

    def __init__(self, name):
        super.__init__(Server_wx)

    def __print_at(self):
        at = self.get_at()
        print(at)
        return at

    def return_at(self):
        at = self.__print_at()
        return at

