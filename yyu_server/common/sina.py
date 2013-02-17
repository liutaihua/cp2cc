#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common.base_httphandler import BaseHandler

from weibo import APIClient


APP_KEY = '4087466243'
APP_SECRET = '14d2e9ef3204a6746df0608ffebce70f'
CALLBACK_URL = 'http://yyu.me/wblogin_check' # callback url

def _get_referer_url(request_handle):
    headers = request_handle.request.headers
    referer_url = headers.get('HTTP_REFERER', '/')
    host = headers.get('Host')
    if referer_url.startswith('http') and host not in referer_url:
        referer_url = '/' # 避免外站直接跳到登录页而发生跳转错误
    return referer_url


class WeiboLoginCheckHandler(BaseHandler):
    def get(self):
        userid = self.get_user_id()
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
        userid = self.get_user_id()
        backurl = self.get_argument('backurl', None)
        print 2222222222222222, userid
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
        userid = self.get_user_id()
        self.clear_cookie('Weibo'+str(userid))
        return self.redirect(referer) if referer else self.redirect('/')
        #self.finish('ok')
