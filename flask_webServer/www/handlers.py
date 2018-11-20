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

import re, time, json, logging, hashlib, base64, asyncio, xmltodict, sys
from datetime import datetime
from models_version_1 import User, ClickEvent, SubscribeEvent, MenuEvent, Message, ViewEvent,\
    Server_wx, Order_wx
from orm_version_1 import execute, select
from flask import Flask, request, redirect, render_template
app = Flask(__name__, static_url_path='')
from PASS_secret import appname_lx, appid_lx, appsecret_lx, token_lx,\
    appname_aijiu, appid_aijiu, appsecret_aijiu, token_aijiu

from gevent import monkey
from gevent.pywsgi import WSGIServer


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
            MenuEvent(menu_id='10014',
                      menu_name=eventkey,
                      menu_event=event,
                      click_num=1,
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
            MenuEvent.execute(menu_id='10015',
                              menu_name=eventkey,
                              menu_event=event,
                              click_num=1,
                              create_time=timestamp)
            result = ow.get_member_info(fromuserName)
            unionId = result['unionid']
            ret = select(sql="select count(distinct referee) as cnt from user_re where referrer = '?'",
                          args=unionId)
            if 'cnt' in ret:
                cnt = ret[0]['cnt']
                text = '您已经推荐成功了%s位成员，请继续努力哦。' % cnt
                result_xml = ow.answer_text(unionId=unionId, touserName=touserName, text=text)
            else:
                logging.WARNING('SqlServer connection failed without result')
                result_xml = ""
            return result_xml
        elif event == 'subscribe':
            fromuserName = resp_dict.get('FromUserName')
            result = ow.get_member_info(fromuserName)
            unionId = result['unionid']
            nickName = result['nickname']
            sex = result['sex']
            city = result['city']
            province = result['province']
            country = result['country']
            t = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
            ret = execute(sql="insert into WXmps.users(?, ?, ?, ?, ?, ?, ?)",
                          args=(unionId, nickName, sex, city, province, country, t))
            if ret:
                logging.info('Has INSERT INTO users table.')
            else:
                logging.WARNING('INSERT Failed.')
            ret = execute(sql="insert into WXmps.subscribe_event(?, ?, ?, ?, ?)",
                          args=(t, event, fromuserName, unionId, t))
            if ret:
                logging.info('Has INSERT INTO subscribe_event table.')
            else:
                logging.WARNING('INSERT Failed.')

            ret = select(sql='select * from Weixin.followers where new_member = "?" ',
                         args=unionId)
            if ret:
                old_t = time.mktime(
                    time.strptime(ret[0]['connect_time'].strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"))
                now_t = time.time()
                old = ret[0]['old_member']
                new = ret[0]['new_member']
                connect_time = ret[0]['connect_time']
                if now_t - old_t <= 600:
                    ret = execute(sql="update Weixin.followers set subscribe_status = ?, update_time = ?, "
                                  "where old_member = ? and new_member = ? and connect_time = ?",
                                  args=('1', t, old, new, connect_time))
                    if ret:
                        logging.info('Has INSERT INTO subscribe_event table.')
                    else:
                        logging.WARNING('INSERT Failed.')

            return ""
        elif event == 'unsubscribe':
            # has been failed which need to be changed.
            fromuserName = resp_dict.get('FromUserName')
            result = ow.get_member_info(fromuserName)
            unionId = result['unionid']
            t = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
            ret = select(sql="select * from Weixin.followers where new_member = '?' order by connect_time desc limit 1",
                   args=unionId)
            if ret:
                old = ret[0]['old_member']
                new = ret[0]['new_member']
                connect_time = ret[0]['connect_time']
                ret_ = execute(sql="update Weixin.followers set subscribe_status = ?, update_time = ?, "
                                   "where old_member = ? and new_member = ? and connect_time = ?",
                               args=('0', t, old, new, connect_time))
                if ret:
                    logging.info('Has INSERT INTO subscribe_event table.')
                else:
                    logging.WARNING('INSERT Failed.')
        else:
            fromuserName = resp_dict.get('FromUserName')
            touserName = resp_dict.get('ToUserName')
            text = '抱歉，自动回复系统正在维护中，将于近日上线，请您谅解。'
            result_xml = ow.answer_text(unionId=fromuserName, touserName=touserName, text=text)
            return result_xml
    else:
        return ""

@app.get('/', methods=['GET'])
def handle_get():
    if 'openid' not in request.args and 'timestamp' in request.args:
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        signature = request.args.get('signature')
        if ow.token_verify(timestamp=timestamp, nonce=nonce, signature=signature):
            logging.info("Token Verify Succeed.")
            return request.args.get('echostr')
        else:
            logging.WARNING("Token Verify Failed.")
            return ""
    elif 'code' in request.args:
        time.sleep(0.5)
        code = request.args.get('code')
        state = request.args.get('state')
        result = ow.get_member_info_by_code(code=code)
        unionId = result['unionid']
        t = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        ret = execute(sql="insert into Weixin.followers(old_member, new_member, connect_time, subscribe_status, "
                          "create_time, update_time values(?, ?, ?, ?, ?, ?)",
                      args=(state, unionId, t, '0', t, t))
        if ret:
            url = 'https://mp.weixin.qq.com/s?__biz=MzUzNDk2ODE3Nw==&mid=100001788&idx=1&sn=3006adb45440eb754dd69a0007447ffb&chksm=7a8de5e24dfa6cf4e452b69133cd0c3cd2195f4ed3e16c46ec291406fc5ef6f0b6605cda40d2&mpshare=1&scene=1&srcid=11147dk6bwNSgStEkFerTnMO#rd'
            return redirect(url)
        else:
            return render_template('index.html')

if __name__ == '__main__':
    handler = logging.FileHandler('flask.log')
    app.logger.addHandler(handler)
    handler.setLevel(logging.DEBUG)
    logging_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    handler.setFormatter(logging_format)
    if len(sys.argv) == 1:
        http_server = WSGIServer(('0.0.0.0'), app)
        http_server.serve_forever()
        # app.run(host="0.0.0.0")
    else:
        port = int(sys.argv[1])
                # app.debug=True
        http_server = WSGIServer(('0.0.0.0', port), app)
        http_server.serve_forever()
        # app.run(host="0.0.0.0", port=port)