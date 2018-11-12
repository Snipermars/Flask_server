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
from orm_version_1 import Base_wx, Model, StringField, BooleanField, FloatField, TextField
from datetime import datetime


def next_id():
    return '%015d%000' % (int(time.time() * 1000), uuid.uuid4().hex)

class User(Model):
    __table__ = 'users'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    nickName = StringField(ddl='varchar(50)')
    Sex = StringField(ddl='varchar(20)')
    City = StringField(ddl='varchar(50)')
    Province = StringField(ddl='varchar(50)')
    Country = StringField(ddl='varchar(50)')
    created_at = StringField(ddl='varchar(50)')

class ClickEvent(Model):
    __table__ = 'clickevent'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    fromuserName = StringField(ddl='varchar(80)')
    clickuserName = StringField(ddl='varchar(80)')
    clickTime = StringField(ddl='varchar(50)')

class Subscibe(Model):
    __table__ = 'subscribe'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    subuserName = StringField(ddl='varchar(80)')
    status = BooleanField()
    created_at = StringField(ddl='varchar(50)')
    update_at = StringField(ddl='varchar(50)')


class UnSubscibe(Model):
    __table__ = 'subscribe'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    subuserName = StringField(ddl='varchar(80)')
    status = BooleanField()
    created_at = StringField(ddl='varchar(50)')
    update_at = StringField(ddl='varchar(50)')

class Message(Model):
    pass

class Server_wx(Base_wx):

    def __init__(self, name):
        super.__init__(Server_wx)

    def __print_at(self):
        at = self.get_at()
        print(at)
        return at

    def return_at(self):
        at = self.__print_at()
        return at

    def get_member_info_by_code(self, code, state):
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

