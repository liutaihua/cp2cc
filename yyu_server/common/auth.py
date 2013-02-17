from common.base_httphandler import BaseHandler
import urllib
import string
from base64 import b64encode

import tornado.auth
from tornado.options import options

from common.util import get_user_db


HOST = options.HOST

class AuthLoginHandler(BaseHandler, tornado.auth.GoogleMixin):
    
    _OPENID_ENDPOINT = "https://www.google.com.hk/accounts/o8/ud"
    _OAUTH_ACCESS_TOKEN_URL = "https://www.google.com.hk/accounts/OAuthGetAccessToken"

    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("openid.mode", None):
            user = self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        ax_attrs=["name", "email", "language", "username"]
        callback_uri = "http://%s%s"%(HOST,self.request.path) 
        args = self._openid_args(callback_uri, ax_attrs=ax_attrs)
        self.redirect(self._OPENID_ENDPOINT + "?hl=zh-CN&" + urllib.urlencode(args))

    def _on_auth(self, user):
        referer = self.request.headers.get('Referer', None)
        if not user:
            raise tornado.web.HTTPError(500, "Google auth failed")
        else:
            name = user['name']
            email = user['email']
            userid = account_new(name, email)
            login(self, userid)
            return self.redirect(referer) if referer else self.redirect('/history')
            #self.redirect('/history')

class AuthLogoutHandler(BaseHandler):
    def get(self):
        logout(self)
        self.write('You are now logged out. '
                   'Click <a href="/account/login">here</a> to log back in.')
        self.redirect('/')


import os
def login(self, userid):
    userid = int(userid)
    print self.session
    s = self.session.get(userid)
    if not s:
        s = os.urandom(12)
        self.session['userid'] = userid
    self.session.save()
    self.set_cookie('userid', b64encode(str(id) + "@@@" + s))

def logout(self):
    if self.get_user_id():
        userid = self.get_user_id()
        if 'userid' in self.session:
            del self.session['userid']
    self.session.save()
    self.clear_cookie('userid')


def account_new(name, email):
    name, email = map(string.strip, (name, email))
    userid = user_id_by_email(email)
    if not userid:
        #cursor = connection.cursor()
        cursor = get_user_db()
        if email:
            cursor.execute(
                '''insert into account (name, email) values ('%s','%s')'''%(name, email)
            )   
        userid = userid_by_email(email)
    return userid


def user_id_by_email(email):
    #cursor = connection.cursor()
    cursor = get_user_db()
    userid = cursor.query("select id from account where email='%s'"%email)
    if userid:
        userid = userid[0]['id']
    else:
        userid = 0 
    return userid
