# !/usr/bin/python3.5
# -*- coding: utf-8 -*-
"""
@ProjectDistribution:
@Time: 2018/10/31 11:26
@Author: Marus
@Function:FlaskWebServer_2.py
"""

import sys
sys.path.append(r'/home/ubuntu/TestingWebServer-master/flask_webServer/config')

from flask import Flask, request, redirect, render_template
import hashlib
import xmltodict
from PIL import Image
import qrcode
import time
import requests
import json
import pymysql
from datetime import datetime
from PASS_secret import appname_lx, appid_lx, appsecret_lx, token_lx,\
    appname_aijiu, appid_aijiu, appsecret_aijiu, token_aijiu\
# from Regex_class import RegexConverter

from gevent import monkey
from gevent.pywsgi import WSGIServer
monkey.patch_all()

app = Flask(__name__, static_url_path='')

appname_server = appname_lx
appid_server = appid_lx
appsecret_server = appsecret_lx
token_server = token_lx

appname_order = appname_aijiu
appid_order = appid_aijiu
appsecret_order = appsecret_aijiu
token_order = token_aijiu

lx_access_token = ''
aijiu_access_token = ''

# 确认数据库链接
conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='lpd.com312', db='WXmps')
cur = conn.cursor(cursor=pymysql.cursors.DictCursor)

# 更新access_token
def get_access_token(at, appid, appsecret):
    resp_check = requests.get(url='https://api.weixin.qq.com/cgi-bin/user/get?access_token={}'.format(at))
    resp_check_dict = json.loads(resp_check.text)
    if 'errcode' in resp_check_dict:
        resp = requests.get(url='https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (appid, appsecret))
        resp_dict = json.loads(resp.text)
        access_token = resp_dict['access_token']
        expires_in = resp_dict['expires_in']
        return access_token
    else:
        return at

# 创建自定义菜单
def post_menu():
    postmenu = """
        {
    	"button": [{
    			"name": "艾灸知识",
    			"sub_button": [{
    					"type": "view",
    					"name": "视频小讲堂",
    					"url": "http://mp.weixin.qq.com/mp/homepage?__biz=MzUzNDk2ODE3Nw==&hid=14&sn=23dfd14f48f9c8ba6c6a195464078a20&scene=18#wechat_redirect"
    				},
    				{
    					"type": "view",
    					"name": "艾灸案例分享",
    					"url": "http://mp.weixin.qq.com/mp/homepage?__biz=MzUzNDk2ODE3Nw==&hid=13&sn=066ad8c914c1de2524e3f875f349a938&scene=18#wechat_redirect"
    				},
    				{
    					"type": "view",
    					"name": "产品合作",
    					"url": "http://mp.weixin.qq.com/mp/homepage?__biz=MzUzNDk2ODE3Nw==&hid=21&sn=4b9c943d1bf43994418aefca8988d198&scene=18#wechat_redirect"
    				},
    				{
    					"type": "click",
    					"name": "个人二维码",
    					"key": "v10014_qrcode"
                    }
    			]
    		},
    		{
    			"name": "病症查找",
    			"sub_button": [{
    					"type": "view",
    					"name": "风心五男",
    					"url": "http://mp.weixin.qq.com/mp/homepage?__biz=MzUzNDk2ODE3Nw==&hid=17&sn=5051af421e6dcea829b1ecbc63d25090&scene=18#wechat_redirect"
    				},
    				{
    					"type": "view",
    					"name": "胃呼妇美",
    					"url": "http://mp.weixin.qq.com/mp/homepage?__biz=MzUzNDk2ODE3Nw==&hid=18&sn=88d90c315ee598e28811f5c4c6be1c73&scene=18#wechat_redirect"
    				},
    				{
    					"type": "view",
    					"name": "神泌儿肿",
    					"url": "http://mp.weixin.qq.com/mp/homepage?__biz=MzUzNDk2ODE3Nw==&hid=19&sn=282c84b31cc2a2364220fcae572bd89f&scene=18#wechat_redirect"
    				},
    				{
    					"type": "view",
    					"name": "疑难杂症",
    					"url": "http://mp.weixin.qq.com/mp/homepage?__biz=MzUzNDk2ODE3Nw==&hid=20&sn=78ffeaf2a6e0a8f2384c224d28159d23&scene=18#wechat_redirect"
    				}
    			]
    		},
    		{
                "type": "view",
                "name": "穴位查询",
                "url": "http://b.92wan.com/12line.html"
            }
        ]
        }"""
    global aijiu_access_token
    access_token = aijiu_access_token
    aijiu_access_token = get_access_token(access_token, appid_order, appsecret_order)
    access_token = aijiu_access_token
    url = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s' % access_token
    resp = requests.post(url, postmenu)
    resp_dict = json.loads(resp.text)
    if resp_dict['errcode'] == 0:
        return 1
    else:
        return 0

# 判断是否是来自微信的请求
def is_from_weixin(kw):
    keys = []
    for k in kw:
        keys.append(k)
    if 'token' in keys and 'timestamp' in keys and 'nonce' in keys and 'signature' in keys:
        args_list = [kw['token'], kw['timestamp'], kw['nonce']]
        args_list.sort()
        mysha = hashlib.sha1()
        map(mysha.update, args_list)
        sha1 = mysha.hexdigest()
        app.logger.debug('%s' % sha1)
        if sha1 == kw['signature']:
            return 1
        else:
            return 0

# 图片合成
def concat_qrcode(pic, is_concat=1):
    pic1 = '/home/ubuntu/awesome-python3-webapp-master/qrcode_png/20181029192714.jpg'
    top_img = pic
    # 缩小图片
    mwidth = 250
    mheight = 250
    top_img_w, top_img_h = top_img.size
    if is_concat == 0:
        return pic
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
    offset = ((bottom_img_w - new_im_w) - 100, (bottom_img_h - new_im_h) - 750)
    # embed top_img on top of bottom_img
    bottom_img.paste(new_im, offset)
    return bottom_img

# 生成二维码图片
def PostQRcode(unionid, appid):
    redirect_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?redirect_uri=http%3A%2F%2Fapi.health.92wan.com%2F&scope=snsapi_userinfo&response_type=code&appid={}&state={}#wechat_redirect'.format(
        appid, unionid)
    qrcode_img = qrcode.make(redirect_url)
    qrcode_result = concat_qrcode(qrcode_img, is_concat=1)
    return qrcode_result

# 二维码图片保存
def SaveQRcode(unionid, appid_order, appsecret_order, appid_server):
    img_dir = '/home/ubuntu/awesome-python3-webapp-master/qrcode_png/'
    img_result = PostQRcode(unionid, appid_server)
    print(img_result)
    if img_result:
        img_path = img_dir + unionid + '_' + appid_order + '.jpg'
        img_result.save(img_path)
        global aijiu_access_token
        access_token = aijiu_access_token
        aijiu_access_token = get_access_token(access_token, appid_order, appsecret_order)
        access_token = aijiu_access_token
        data = {'media': open(img_path, 'rb')}
        postdata = {
            'media': (img_path, open(img_path, 'rb'), 'image/jpg')
        }
        resp = requests.post(
            'https://api.weixin.qq.com/cgi-bin/media/upload?access_token={}&type={}'.format(access_token, 'image/jpg'),
            files=postdata)
        resp_dict = json.loads(resp.text)
        print(resp_dict)
        if 'media_id' in resp_dict:
            return resp_dict['media_id'], resp_dict['created_at']
        else:
            return resp_dict['errcode'], resp_dict['errmsg']
    else:
        return '', ''

# 菜单时间处理
def QrCode_order(resp_dict, event='CLICK', key='v10004_qrcode', appid_server=None, appid_order=None, appsecret_order=None):
    if event != 'CLICK' and key != 'v10004_qrcode':
        return ''
    else:
        touserName = resp_dict.get('ToUserName')
        fromuserName = resp_dict.get('FromUserName')
        # 根据openid获取unionid
        global aijiu_access_token
        access_token = aijiu_access_token
        aijiu_access_token = get_access_token(access_token, appid_order, appsecret_order)
        print(aijiu_access_token+', '+fromuserName)
        result = requests.get('https://api.weixin.qq.com/cgi-bin/user/info?access_token={}&openid={}'.format(aijiu_access_token, fromuserName))
        result_dict = json.loads(result.text)
        print(result_dict)
        unionId = result_dict['unionid']
        media_id, created_at = SaveQRcode(unionId, appid_order, appsecret_order, appid_server)
        if media_id:
            result_xml = """
                <xml>
                <ToUserName>{}</ToUserName>
                <FromUserName>{}</FromUserName>
                <CreateTime>{}</CreateTime>
                <MsgType>{}</MsgType>
                <Image><MediaId>{}</MediaId></Image>
                </xml>
            """.format(fromuserName, touserName, time.time(), 'image', media_id)
        else:
            result_xml = """
                <xml>
                <ToUserName>{}</ToUserName>
                <FromUserName>{}</FromUserName>
                <CreateTime>{}</CreateTime>
                <MsgType>{}</MsgType>
                <Content></Content>
                </xml>
            """.format(fromuserName, touserName, time.time(), 'text', 'Fail to create the qrcode.Please create again!')
        return result_xml

# 请求预处理
@app.before_request
def mydirect():
    import re
    re_likephp = re.compile('(.*?).php')
    if re.search(request.path):
        return ""
    else:



# 获取菜单点击事件
@app.route('/', methods=['POST'])
def clickHandler():
    timestamp = request.args.get('timestamp')
    global appid_order
    global appsecret_order
    global appid_server
    global token_order
    appid_o = appid_order
    appid_s = appid_server
    appsecret_o = appsecret_order
    token_o = token_order
    nonce = request.args.get('nonce')
    signature = request.args.get('signature')
    args_order = {'token': token_o, 'timestamp': timestamp, 'nonce': nonce, 'signature': signature}
    print(args_order)
    if is_from_weixin(args_order): #  and not is_from_weixin(args_server):
        resp_data = request.data
        resp_dict = xmltodict.parse(resp_data).get('xml')
        event = resp_dict.get('Event')
        eventkey = resp_dict.get('EventKey')
        if event == 'CLICK' and eventkey == 'v10004_qrcode':
            result_xml = QrCode_order(resp_dict=resp_dict, appid_server=appid_s,\
                                      appid_order=appid_o, appsecret_order=appsecret_o)
            return result_xml
        elif resp_dict.get('Event') == 'subscribe':
            fromuserName = resp_dict.get('FromUserName')
            global aijiu_access_token
            access_token = aijiu_access_token
            aijiu_access_token = get_access_token(access_token, appid_o, appsecret_o)
            access_token = aijiu_access_token
            print(access_token)
            resp2 = requests.get('https://api.weixin.qq.com/cgi-bin/user/info?access_token={}&openid={}'.format(access_token, fromuserName))
            resp_dict2 = json.loads(resp2.text)
            unionId = resp_dict2['unionid']
            nickName = resp_dict2['nickname']
            Sex = resp_dict2['sex']
            city = resp_dict2['city']
            province = resp_dict2['province']
            country = resp_dict2['country']
            t = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
            cur.execute(
                "insert into WXmps.aijiu_member(OpenId, UnionId, update_time) values(%s,%s,%s)", (str(fromuserName), str(unionId), t))
            cur.execute(
                "insert into WXmps.aijiu_member_info(OpenId, UnionId, NickName, Sex, City, Province, Country, update_time) "\
                "values(%s, %s, %s, %s, %s, %s, %s, %s)", (str(fromuserName), str(unionId), nickName, Sex, city,\
                                                         province, country, t))
            conn.commit()
            cur.execute(
                "select * from WXmps.followers where new_member = '%s' order by connect_time desc limit 1" % str(
                    unionId))
            ret = cur.fetchall()
            if ret:
                old_t = time.mktime(time.strptime(ret[0]['connect_time'].strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"))
                now_t = time.time()
                old = ret[0]['old_member']
                new = ret[0]['new_member']
                connect_time = ret[0]['connect_time']
                if now_t - old_t <= 600:
                    cur.execute(
                        "UPDATE WXmps.followers set subscribe_status = '1', update_time = '%s'"\
                        "WHERE old_member = '%s' and new_member = '%s' and connect_time = '%s'" % (t, old, new, connect_time))
                conn.commit()
                return ""
            else:
                return ""
        elif resp_dict.get('Event') == 'unsubscribe':
            fromuserName = resp_dict.get('FromUserName')
            global aijiu_access_token
            access_token = aijiu_access_token
            aijiu_access_token = get_access_token(access_token, appid_o, appsecret_o)
            access_token = aijiu_access_token
            resp2 = requests.get(
                'https://api.weixin.qq.com/cgi-bin/user/info?access_token={}&openid={}'.format(access_token,
                                                                                               fromuserName))
            resp_dict2 = json.loads(resp2.text)
            unionId = resp_dict2['unionid']
            t = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
            cur.execute("select * from WXmps.followers where new_member = '%s'" % str(unionId))
            ret = cur.fetchall()
            print(ret)
            if ret:
                old = ret[0]['old_member']
                new = ret[0]['new_member']
                connect_time = ret[0]['connect_time']
                cur.execute("UPDATE WXmps.followers set subscribe_status = '0', update_time = '%s'"\
                            " WHERE old_member = '%s' and new_member = '%s' and connect_time = '%s';" % (t, old, new, connect_time))
                conn.commit()
                return ""
            else:
                return ""
        else:
            return ""
    else:
        return ""


# 微信验证
@app.route('/', methods=['GET'])
def index():
    """
    if 'code' not in request.args and 'timestamp' in request.args:
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        signature = request.args.get('signature')
        args_server = {'token': token_s, 'timestamp': timestamp, 'nonce': nonce, 'signature': signature}
        args_order = {'token': token_o, 'timestamp': timestamp, 'nonce': nonce, 'signature': signature}
        if is_from_weixin(args_order):
            return request.args.get('echostr')
        elif is_from_weixin(args_order):
            return request.args.get('echostr')
        else:
            return ""
    """
    if 'code' in request.args:
        time.sleep(1)
        code = request.args.get('code')
        state = request.args.get('state')
        data = {
            'grant_type': 'authorization_code',
            'appid': appid_server,
            'code': code,
            'secret': appsecret_server
            }
        url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        resp = requests.get(url, params=data)
        resp_dict = json.loads(resp.text)
        print(resp_dict)
        unionId = resp_dict['unionid']
        t = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        cur.execute("insert into WXmps.followers(old_member, new_member, connect_time, subscribe_status, create_time, update_time) values(%s,%s,%s,%s,%s,%s)", (str(state), str(unionId), t, "0", t, t))
        conn.commit()
        # 判断是否关注应该在另一个维度
        # url = 'https://mp.weixin.qq.com/s?__biz=MzUzNDk2ODE3Nw==&mid=100001640&idx=1&sn=5334d2ec5424bdc9b664e015ff337ac3&chksm=7a8de5764dfa6c6017d8710e114839d40bb915dc5113fb1a307f6d3a2666efa8939e18f3636b&mpshare=1&scene=1&srcid=10264CB412pHCzOtGsCsz7c1#rd'
        # url = 'https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzUzNDk2ODE3Nw==&chksm==&scene=110#wechat_redirect'
        url = 'https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzUzNDk2ODE3Nw==&wechat_webview_type=1&#wechat_redirect'
        # url = 'https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzU5ODczMTYxNA==&chksm==&scene=110#wechat_redirect'
        return redirect(url)
    else:
        return render_template('index.html')

# app.url_map.converters['regex'] = RegexConverter
# @app.route('/<regex("[a-z]{3}"):user_id>.php', methods=['GET'])
# def FilterErrorRequest(param):
#    if param:
#        return ""

if __name__ == '__main__':
    if len(sys.argv) == 1:
        http_server = WSGIServer(('0.0.0.0'), app)
        http_server.server_forever()
        # app.run(host="0.0.0.0")
    else:
        port = int(sys.argv[1])
                # app.debug=True
        http_server = WSGIServer(('0.0.0.0', port), app)
        http_server.server_forever()
        # app.run(host="0.0.0.0", port=port)