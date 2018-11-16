# !/usr/bin/python3.5
# -*- coding: utf-8 -*-
"""
@ProjectDistribution:
@Time: 2018/11/8 9:56
@Author: Marus
@Function:orm_version_1.py
"""

import asyncio, aiomysql
import logging
import requests
import json
import hashlib
import time
from datetime import datetime
logging.basicConfig(level=logging.INFO)

class Base_wx(object):
    """
    create the metaclass for weixin_mps
    """
    def __init__(self, appid, appname, appsecret, apptoken, appencodingasekey):
        self.__appId = appid
        self.__appName = appname
        self.__appSecret = appsecret
        self.__appToken = apptoken
        self.__appEncodingASEKey = appencodingasekey
        self.__access_token = ''
        self.__init_time = 0
        self.now_time = 0

    def get_attr(self):
        """
        :return: three parameters which are appid, appsecret, apptoken
        """
        return self.__appId, self.__appSecret, self.__appToken

    def token_verify(self, timestamp, nonce, signature):
        """
        token verify for server or order
        :return: 1 or 0
        """
        args_list = [self.__appToken, timestamp, nonce]
        args_list.sort()
        mysha = hashlib.sha1()
        map(mysha.update, args_list)
        sha1 = mysha.hexdigest()
        if sha1 == signature:
            return 1
        else:
            return 0

    def verify_at(self):
        """
        :return: boolean whether to update the access_token
        """
        if self.__access_token:
            return 1
        else:
            resp = requests.get('https://api.weixin.qq.com/cgi-bin/user/get?access_token={}'.format
                                (self.__access_token))
            if 'errcode' in resp.text:
                return 1
            else:
                return 0

    def update_at(self):
        """
        :return:
        """
        if not isinstance(int(str((self.now_time - self.__init_time)/7200.0)), int) and self.verify_at():
            resp = requests.get(url='https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&'\
                                    'secret=%s' % (self.__appId, self.__appSecret))
            resp_dict = json.loads(resp.text)
            self.__access_token = resp_dict['access_token']
            return self.__access_token
        elif isinstance(int(str((self.now_time - self.__init_time)/7200.0)), int):
            resp = requests.get(url='https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&' \
                                    'secret=%s' % (self.__appId, self.__appSecret))
            resp_dict = json.loads(resp.text)
            self.__access_token = resp_dict['access_token']
            return self.__access_token
        else:
            return self.__access_token

    def get_at(self):
        """
        :return: available access_token
        """
        access_token = self.update_at()
        return access_token

    def get_member_info(self, openId):
        at = self.get_at()
        resp = requests.get('https://api.weixin.qq.com/cgi-bin/user/info?access_token={}&openid={}'.format(at,
                                                                                                    openId))
        resp_dict = json.loads(resp)
        return resp_dict

    def get_member_list(self):
        """
        :return: available member list(openId)
        """
        at = self.get_at()
        resp = requests.get('https://api.weixin.qq.com/cgi-bin/user/info?access_token={}'.format(at))
        resp_dict = json.loads(resp)
        return resp_dict['data']

    def post_picture(self, img_path):
        """
        save the picture as the temporary material.
        :return:
        """
        at = self.get_at()
        postdata = {
            'media': (img_path, open(img_path, 'rb'), 'image/jpg')
        }
        resp = requests.post(
            'https://api.weixin.qq.com/cgi-bin/media/upload?access_token={}&type={}'.format(at, 'image/jpg'),
            files=postdata)
        resp_dict = json.loads(resp.text)
        if 'media_id' in resp_dict:
            return resp_dict['media_id'], resp_dict['created_at']
        else:
            return resp_dict['errcode'], resp_dict['errmsg']

    def answer_picture(self, unionId, touserName, img_path):
        media_id, created_at = self.post_picture(img_path)
        if media_id:
            result_xml = """
                <xml>
                <ToUserName>{}</ToUserName>
                <FromUserName>{}</FromUserName>
                <CreateTime>{}</CreateTime>
                <MsgType>{}</MsgType>
                <Image><MediaId>{}</MediaId></Image>
                </xml>
            """.format(unionId, touserName, time.time(), 'image', media_id)
        else:
            result_xml = """
                <xml>
                <ToUserName>{}</ToUserName>
                <FromUserName>{}</FromUserName>
                <CreateTime>{}</CreateTime>
                <MsgType>{}</MsgType>
                <Content></Content>
                </xml>
            """.format(unionId, touserName, time.time(), 'text', 'Fail to create the qrcode.Please create again!')
        return result_xml

    def answer_text(self, unionId, touserName, text):
        if text:
            result_xml = """
                <xml>
                <ToUserName>{}</ToUserName>
                <FromUserName>{}</FromUserName>
                <CreateTime>{}</CreateTime>
                <MsgType>{}</MsgType>
                <Image><MediaId>{}</MediaId></Image>
                </xml>
            """.format(unionId, touserName, time.time(), 'text', text)
        else:
            result_xml = """
                <xml>
                <ToUserName>{}</ToUserName>
                <FromUserName>{}</FromUserName>
                <CreateTime>{}</CreateTime>
                <MsgType>{}</MsgType>
                <Content></Content>
                </xml>
            """.format(unionId, touserName, time.time(), 'text',  'Fail to answer text.Please create again!')
        return result_xml

    def answer_url(self, unionId, touserName, url):
        if url:
            result_xml = """
                <xml>
                <ToUserName>{}</ToUserName>
                <FromUserName>{}</FromUserName>
                <CreateTime>{}</CreateTime>
                <MsgType>{}</MsgType>
                <Image><MediaId>{}</MediaId></Image>
                </xml>
            """.format(unionId, touserName, time.time(), 'url', url)
        else:
            result_xml = """
                <xml>
                <ToUserName>{}</ToUserName>
                <FromUserName>{}</FromUserName>
                <CreateTime>{}</CreateTime>
                <MsgType>{}</MsgType>
                <Content></Content>
                </xml>
            """.format(unionId, touserName, time.time(), 'text', 'Fail to answer url.Please create again!')
        return result_xml

    def answer_auto(self, resp_dict, result):
        """
        :param resp_dict:
        :param type:
        :return:
        """
        at = self.get_at()
        touserName = resp_dict.get('ToUserName')
        fromuserName = resp_dict.get('FromUserName')
        result = requests.get('https://api.weixin.qq.com/cgi-bin/user/info?access_token={}&openid={}'.format(at, fromuserName))
        result_dict = json.loads(result)
        unionId = result_dict['unionid']
        if result == 'url':
            url = ''
            return self.answer_url(unionId, touserName, url)
        elif result == 'text':
            text = ''
            return self.answer_text(unionId, touserName, text)
        elif result == 'img':
            img_path = ''
            return self.answer_picture(unionId, touserName, img_path)
        pass

def log(sql, args=()):
    logging.info('SQL: %s' % sql)

async def create_pool(loop, **kw):
    logging.info('create database connection pool...')
    global __pool
    __pool = await aiomysql.create_pool(
        host=kw.get('host', '192.168.222.128'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop
    )

async def select(sql, args, size=None):
    log(sql, args)
    global __pool
    async with __pool.get() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql.replace('?', '%s'), args or ())
            if size:
                rs = await cur.fetchmany(size)
            else:
                rs = await cur.fetchall()
        logging.info('rows returned: %s' % len(rs))
        return rs

async def execute(sql, args, autocommit=True):
    log(sql)
    async with __pool.get() as conn:
        if not autocommit:
            await conn.begin()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace('?', '%s'), args)
                affected = cur.rowcount
            if not autocommit:
                await conn.commit()
        except BaseException as e:
            if not autocommit:
                await conn.rollback()
            raise
        return affected

def create_args_string(num):
    L = []
    for n in range(num):
        L.append('?')
    return ', '.join(L)

class Field(object):

    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)

class StringField(Field):

    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)

class BooleanField(Field):

    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)

class IntegerField(Field):

    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'bigint', primary_key, default)

class FloatField(Field):

    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'real', primary_key, default)

class TextField(Field):

    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)

class DateTimeField(Field):

    def __init__(self, name=None, default=datetime.now):
        super().__init__(name, 'datetime', False, default)

class DateField(Field):

    def __init__(self, name=None, default=datetime.now):
        super().__init__(name, 'date', False, default)

class ModelMetaclass(type):

    def __new__(mcs, name, bases, attrs):
        if name == 'Model':
            return type.__new__(mcs, name, bases, attrs)
        tableName = attrs.get('__table__', None) or name
        logging.info('found model: %s (table: %s)' % (name, tableName))
        mappings = dict()
        fields = []
        primaryKey = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                logging.info('  found mapping: %s ==> %s' % (k, v))
                mappings[k] = v
                if v.primary_key:
                    # 找到主键:
                    if primaryKey:
                        raise BaseException('Duplicate primary key for field: %s' % k)
                    primaryKey = k
                else:
                    fields.append(k)
        if not primaryKey:
            raise BaseException('Primary key not found.')
        for k in mappings.keys():
            attrs.pop(k)
        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        attrs['__mappings__'] = mappings  # 保存属性和列的映射关系
        attrs['__table__'] = tableName
        attrs['__primary_key__'] = primaryKey  # 主键属性名
        attrs['__fields__'] = fields  # 除主键外的属性名
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (primaryKey, ', '.join(escaped_fields), tableName)
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (tableName, ', '.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName, ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)
        return type.__new__(mcs, name, bases, attrs)

class Model(dict, metaclass=ModelMetaclass):

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s: %s' % (key, str(value)))
                setattr(self, key, value)
        return value

    @classmethod
    async def findAll(cls, where=None, args=None, **kw):
        """ find objects by where clause. """
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        orderBy = kw.get('orderBy', None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
        limit = kw.get('limit', None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s' % str(limit))
        rs = await select(' '.join(sql), args)
        return [cls(**r) for r in rs]

    @classmethod
    async def findNumber(cls, selectField, where=None, args=None):
        ''' find number by select and where. '''
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = await select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    @classmethod
    async def find(cls, pk):
        ''' find object by primary key. '''
        rs = await select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    async def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = await execute(self.__insert__, args)
        if rows != 1:
            logging.WARN('failed to insert record: affected rows: %s' % rows)

    async def update(self):
        args = list(map(self.getValue, self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        rows = await execute(self.__update__, args)
        if rows != 1:
            logging.WARN('failed to update by primary key: affected rows: %s' % rows)

    async def remove(self):
        args = [self.getValue(self.__primary_key__)]
        rows = await execute(self.__delete__, args)
        if rows != 1:
            logging.WARN('failed to remove by primary key: affected rows: %s' % rows)