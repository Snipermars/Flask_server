# -*- coding: utf-8 -*-

#!/usr/bin/python

import sys
from flask import Flask, request, redirect, make_response, jsonify, render_template, send_file
import hashlib
import xmltodict
import time
from PIL import Image
import qrcode
import time 
import requests
import json
import pymysql
from datetime import datetime 

app = Flask(__name__, static_folder='static')

appid = 'wxce5b61cfd901d76e'
appsecret = '36d31dfe75389dfa3cc47152b6e6dca9'
now_access_token = ''

# 连接数据库保存
conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='lpd.com312', db='WXmps')
cur = conn.cursor(cursor=pymysql.cursors.DictCursor)

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
    					"key": "v10004_qrcode"
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
    global now_access_token
    access_token = now_access_token
    now_access_token = get_access_token(access_token, appid, appsecret)
    access_token = now_access_token
    url = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s' % access_token
    resp = requests.post(url, postmenu)
    resp_dict = json.loads(resp.text)
    if resp_dict['errcode'] == 0:
        return 1
    else:
        return 0


# 二维码图片生成
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

# 等待扫码事件发生
# 扫码事件发生, 获取请求者指定参数(state为原推送者个人open_id)
def get_redirect_url(appid, param, is_info=0):
    pre_url = 'http://api.health.92wan.com/'
    appid = appid
    scope = 'snsapi_userinfo' if is_info else 'snsapi_base'
    data = {'redirect_uri': pre_url,
            'appid': appid,
            'response_type': 'code',
            'scope': scope,
            'state': param}
    urlencode = urllib.urlencode(data)
    wei_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?' + urlencode + '#wechat_redirect'
    return wei_url
    
def get_user_status(openId, access_token):
    resp = requests.get('https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s&lang=zh_CN' %(access_token, openId))
    resp_dict = json.loads(resp.text)
    return resp_dict 
    
def Subscribed(openId):
    resp = requests.get('https://mp.weixin.qq.com/s/cd6iNh8XSBjly08DXGJ_tA')
    return resp.content
# 这个页面在服务器上同样打不开。
def Unsubscribed(openId):
    resp = requests.get('https://mp.weixin.qq.com/s/cd6iNh8XSBjly08DXGJ_tA')
    return resp.content
    
def get_access_token(at, appid, appsecret):
    print(at)
    resp_check = requests.get(url='https://api.weixin.qq.com/cgi-bin/user/get?access_token={}'.format(at))
    resp_check_dict = json.loads(resp_check.text)
    if 'errcode' in resp_check_dict and resp_check_dict['errcode'] == 41001:
        resp = requests.get(url='https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (appid, appsecret))
        resp_dict = json.loads(resp.text)
        print(resp_dict)
        access_token = resp_dict['access_token']
        expires_in = resp_dict['expires_in']
        return  access_token 
    else:
        return at 

# 获取菜单点击事件openid
# 根据openid和回调地址生成个人二维码图片
def PostQRcode(openid, appid):
    redirect_uri = 'http://api.health.92wan.com/'
    if appid == 'wxce5b61cfd901d76e':  # 订阅号
        redirect_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?redirect_uri=http%3A%2F%2Fapi.health.92wan.com%2F&scope=snsapi_base&response_type=code&appid={}&state={}#wechat_redirect'.format(appid, openid)
        qrcode_img = qrcode.make(redirect_url)
        qrcode_result = concat_qrcode(qrcode_img, is_concat=1)
        return qrcode_result
    else:
        return ''
        
def SaveQRcode(openid, appid):
    img_dir = '/home/ubuntu/awesome-python3-webapp-master/qrcode_png/'
    img_result = PostQRcode(openid, appid)
    print(img_result)
    if img_result:
        img_path = img_dir + openid + '_' + appid + '.jpg'
        img_result.save(img_path)
        global now_access_token
        access_token = now_access_token
        print(access_token)
        now_access_token = get_access_token(access_token, appid, appsecret)
        access_token = now_access_token
        data = {'media': open(img_path, 'rb')}
        postdata = {
            'media': (img_path, open(img_path, 'rb'), 'image/jpg')
            }
        resp = requests.post('https://api.weixin.qq.com/cgi-bin/media/upload?access_token={}&type={}'.format(access_token, 'image/jpg'), files=postdata)
        resp_dict = json.loads(resp.text)
        print(resp_dict)
        if 'media_id' in resp_dict:
            return resp_dict['media_id'], resp_dict['created_at']
        else:
            return resp_dict['errcode'], resp_dict['errmsg']
    else:
        return '', ''
        
def is_subscribe(old_openId, new_openId, input_t):
    """
    param:
    old_openId: 推广者 openId
    new_openId: 被推广者 openId
    input_t: 被推广者扫描微信时间
    """
    now = time.time()
    user_status_dict = get_user_status(access_token, openId)
    if now - input_t < 3600 and user_status_dict['subscribe'] == 0:
        return '1'
    else:
        return '0'
"""
def perform_subscribe(ole_openId, new_openId, input_t, inc):
    while is_subscribe(ole_openId, new_openId, input_t) == '1':
        s.enter(inc,0,perform_subscribe,(ole_openId, new_openId, input_t, inc))
        is_subscribe(ole_openId, new_openId, input_t)
    
        

def subscribe_main(ole_openId, new_openId, input_t, inc=5):
    s.enter(0,0,perform_subscribe,(ole_openId, new_openId, input_t, inc))
    s.run()
"""            
# 微信验证
@app.route('/', methods=['GET'])
def index():
    token = 'sx0887415157970563ahpandasslexsa'
    if 'code' not in request.args and 'timestamp' in request.args:
        args_list = [token, request.args.get('timestamp'), request.args.get('nonce')]
        args_list.sort()
        mysha = hashlib.sha1()
        map(mysha.update, args_list)
        sha1 = mysha.hexdigest()
        app.logger.debug('%s' % sha1)
        if sha1 == request.args.get('signature'):
            return request.args.get('echostr')
        else:
            return ""
    elif 'code' in request.args:
        time.sleep(2)
        code = request.args.get('code')
        state = request.args.get('state')
        data = {
            'grant_type': 'authorization_code', 
            'appid': appid,
            'code': code,
            'secret': appsecret
            }
        # print(data)
        url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        resp = requests.get(url, params=data)
        resp_dict = json.loads(resp.text)
        print(resp_dict)
        openId = resp_dict['openid']
        global now_access_token
        access_token = now_access_token
        now_access_token = get_access_token(access_token, appid, appsecret)
        access_token = now_access_token
        t = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        cur.execute("insert into WXmps.followers(old_member, new_member, connect_time, subscribe_status, create_time, update_time) values(%s,%s,%s,%s,%s,%s)", (str(state), str(openId), t, "0", t, t))
        conn.commit()
        # 判断是否关注应该在另一个维度
        # url = 'https://mp.weixin.qq.com/s?__biz=MzUzNDk2ODE3Nw==&mid=100001640&idx=1&sn=5334d2ec5424bdc9b664e015ff337ac3&chksm=7a8de5764dfa6c6017d8710e114839d40bb915dc5113fb1a307f6d3a2666efa8939e18f3636b&mpshare=1&scene=1&srcid=10264CB412pHCzOtGsCsz7c1#rd'
        # url = 'https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzUzNDk2ODE3Nw==&chksm==&scene=110#wechat_redirect'
        url = 'https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzU5ODczMTYxNA==&chksm==&scene=110#wechat_redirect'
        return redirect(url) 
        # if user_status_dict['subscribe']:
        #    result = Subscribed(openId)
        # else:
        #     result = Unsubscribed(openId)
        # return result 
    else:
        return render_template('index.html')

@app.route('/{param}.php', methods=['GET'])
def FilterErrorRequest(param):
    if param:
        return ""

# 图片回传给菜单点击事件发送者
@app.route('/', methods=['POST'])    
def GetClickOpenId():
    token = 'sx0887415157970563ahpandasslexsa'
    args_list = [token, request.args.get('timestamp'), request.args.get('nonce')]
    args_list.sort()
    mysha = hashlib.sha1()
    map(mysha.update, args_list)
    sha1 = mysha.hexdigest()
    app.logger.debug('%s' % sha1)
    if sha1 == request.args.get('signature'):
        resp_data = request.data
        resp_dict = xmltodict.parse(resp_data).get('xml')
        if resp_dict.get('Event') == 'CLICK' and resp_dict.get('EventKey') == 'v10004_qrcode':
            touserName = resp_dict.get('ToUserName')
            fromuserName = resp_dict.get('FromUserName')
            createTime = resp_dict.get('createTime')
            msgType = resp_dict.get('MsgType')
            event = resp_dict.get('Event')
            eventKey = resp_dict.get('EventKey')
            media_id, created_at = SaveQRcode(fromuserName, appid)
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
        elif resp_dict.get('Event') == 'VIEW':
            touserName = resp_dict.get('ToUserName')
            fromuserName = resp_dict.get('FromUserName')
            createTime = resp_dict.get('CreateTime')
            msgType = resp_dict.get('MsgType')
            eventKey = resp_dict.get('EventKey')
            menuID = resp_dict.get('MenuID')
            print(resp_dict)
            return ""
        elif resp_dict.get('Event') == 'subscribe':
            fromuserName = resp_dict.get('FromUserName')
            t = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
            cur.execute("select * from WXmps.followers where new_member = '%s' order by connect_time desc limit 1" % str(fromuserName))
            ret = cur.fetchall()
            print(ret)
            if ret:
                old_t = time.mktime(time.strptime(ret[0]['connect_time'].strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"))
                now_t = time.time()
                old = ret[0]['old_member']
                new = ret[0]['new_member']
                if now_t - old_t <= 600:
                    cur.execute("UPDATE WXmps.followers set subscribe_status = '1', update_time = '%s' WHERE old_member = '%s' and new_member = '%s';" % (t, old, new))
                conn.commit()
                return ""
            else:
                return ""
        elif resp_dict.get('Event') == 'unsubscribe':
            fromuserName = resp_dict.get('FromUserName')
            t = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
            cur.execute("select * from WXmps.followers where new_member = '%s'" % str(fromuserName))
            ret = cur.fetchall()
            print(ret)
            if ret:
                old = ret[0]['old_member']
                new = ret[0]['new_member']
                cur.execute("UPDATE WXmps.followers set subscribe_status = '0', update_time = '%s' WHERE old_member = '%s' and new_member = '%s';" % (t, old, new))
                conn.commit()
                return ""
            else:
                return ""
        else:
            return ""
    else:
        return ""

if __name__ == '__main__':
    if len(sys.argv) == 1:
        app.run(host="0.0.0.0")
    else:
        port = int(sys.argv[1])
                # app.debug=True
        app.run(host="0.0.0.0", port=port)
    