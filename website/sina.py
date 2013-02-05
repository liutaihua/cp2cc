#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pylibmc as memcache
from tornado.options import options
import tornado.web
from common.base_httphandler import BaseHandler

from weibo import APIClient


session_mc = ['127.0.0.1:11213']

session_mc_client = memcache.Client(session_mc)
APP_KEY = '4087466243'
APP_SECRET = '14d2e9ef3204a6746df0608ffebce70f'
CALLBACK_URL = 'http://180.153.136.14:8888/wblogin_check' # callback url

def _get_referer_url(request_handle):
    headers = request_handle.request.headers
    referer_url = headers.get('HTTP_REFERER', '/')
    host = headers.get('Host')
    if referer_url.startswith('http') and host not in referer_url:
        referer_url = '/' # 避免外站直接跳到登录页而发生跳转错误
    return referer_url


class WeiboLoginCheckHandler(BaseHandler):
    def get(self):
        userid = self.get_current_userid()
        code = self.get_argument('code', None)
        backurl = self.get_cookie('backurl'+str(userid), None)
        if not code:
            return self.redirect('/sina_oauth')
        client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
        r = client.request_access_token(code)
        access_token = r.access_token
        expires_in = r.expires_in
        self.set_cookie('Weibo'+str(userid), access_token)
        client.set_access_token(access_token, expires_in)
        if backurl:
            return self.redirect('/'+backurl)
        return self.redirect('/history')


class SinaOAuthHandler(BaseHandler):
    def get(self):
        userid = self.get_current_userid()
        backurl = self.get_argument('backurl', None)
        self.set_cookie('backurl'+str(userid), backurl)
        client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
        url = client.get_authorize_url()
        return self.redirect(url)

class AuthLogoutHandler(BaseHandler):
    def get(self):
        pass


class WeiboLogOutCheckHandler(BaseHandler):
    def get(self):
        referer = self.request.headers.get('Referer', None)
        userid = self.get_current_userid()
        self.clear_cookie('Weibo'+str(userid))
        return self.redirect(referer) if referer else self.redirect('/')
        #self.finish('ok')
