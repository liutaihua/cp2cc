#coding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import bz2
import pylibmc
import urllib2
import urllib
import base64


import tornado
import tornado.options
import tornado.web
import tornado.autoreload
from tornado.options import options


import config
import common.session
from common.base_httphandler import BaseHandler
from auth import AuthLoginHandler, AuthLogoutHandler
from sina import SinaOAuthHandler, WeiboLoginCheckHandler, WeiboLogOutCheckHandler


from common.util import get_user_db, get_mc


from tools import txt_get, txt_set, txt_save, txt_by_url, url_random, url_new, get_txt_list, get_url_list_by_userid, url_delete, check_if_name_exists, change_url,\
                  add_pwd_for_url, handle_request_without_ioloop, handle_request

import tornado.httpclient
import urllib

HOST = options.HOST

UPLOAD_WEIBO_URL = 'https://api.weibo.com/2/statuses/update.json'

class MainHandler(BaseHandler):
    def get(self, url):
        '''搞一个判断是否从/web_logincheck过来的http referer, 如果是就传个参数给前端, 前端提示一个微薄认证已成功的淡出提示'''
        referer = self.request.headers.get('Referer', None)
        userid = self.get_current_userid()
        LOGIN = True if self.get_current_userid() else ''
        weibo = True if self.get_cookie('Weibo'+str(userid), None) and referer and LOGIN else ''
        if url == '':
            self.redirect(url_random())
        else:
            #print self.request.headers['User-Agent']
            id = url_new(url)
            txt = txt_get(id)
        self.render('website/show.html', res = txt, href="http://myapp.com/"+url, login=LOGIN, url=url, weibo_login=weibo)
            
            


class TxtHandler(BaseHandler):
    def get(self, url):
        if url == '':
            if self.get_secure_cookie('user'):
                user_name = eval(self.get_secure_cookie('user'))['name']
                if get_txt_list(user_name):
                    self.finish(get_txt_list(user_name))
                else:
                    self.finish('nothing')
        else:
            id = url_new(url)
            txt = txt_get(id)
            if txt:
                self.finish(txt)

    def post(self, url):
        txt_dict = self.request.files
        txt = txt_dict['file'][0]['body']
        txt = bz2.decompress(txt)
        if url == '':
            url = url_random()
            txt_save(url, txt) 
            self.finish(url)
        else:
            txt_save(url, txt) 
            self.finish(url)


class UpdateContentHandler(BaseHandler):
    def get(self, url):
        pass

    def post(self, url):
        userid = self.get_current_userid()
        update_content = urllib2.unquote(self.request.body.split('contents=')[1].split('&')[0])
#        id = url_new(url)
        txt_save(url, txt=update_content, userid=userid)
        self.finish(url)
        


class DeleteHandler(BaseHandler):
    def post(self):
        url = self.get_argument('myurl')
        url_delete(url)
        self.redirect('/history')

class HistoryHandler(BaseHandler):
    def get(self):
        userid = self.get_current_userid()
        print userid
        if userid:
            LOGIN = True
            url_list = get_url_list_by_userid(userid)
            #pretty_url_list = map(lambda x:"http://tt:8888/"+x, url_list)
        else:
            LOGIN = False
            url_list = []
        return self.render('website/history.html', url_list=url_list, href="http://myapp.com/", login=LOGIN)

class CheckUrlExistHandler(BaseHandler):
    def post(self, url):
        res = check_if_name_exists(url)
        res = 'true' if res else 'false'
        return self.finish(res)

class ChangeUrlHandler(BaseHandler):
    def post(self, old_url):
        new_url = self.get_argument('new_url')
        url_id = url_new(old_url)
        change_url(url_id, new_url)
        self.redirect('/'+new_url)

class AddPwdHandler(BaseHandler):
    def post(self, url):
        password = self.get_argument('password')
        encrypt_pwd = add_pwd_for_url(url)
        self.set_cookie('url', encrypt_pwd)
        self.redirect('/'+url)
        
class UploadWeiboHandler(BaseHandler):
    def get(self, url):
        #return self.redirect('/'+url)
        userid = self.get_current_userid()
        http_client = tornado.httpclient.AsyncHTTPClient()
        access_token = self.get_cookie('Weibo'+str(userid), None)
        if not access_token:
            return self.redirect('/wblogin_check')
        #weibo_content = 'Share my note ' + 'http://' + HOST + url
        weibo_content = '一个测试微博, 抱歉打扰到您' + 'http://' + HOST + '/' + url
        data = urllib.urlencode(dict(access_token=access_token, status=weibo_content))
        req = tornado.httpclient.HTTPRequest(url = UPLOAD_WEIBO_URL, method='POST', body=data)
        if not tornado.ioloop.IOLoop.instance().running():
            http_client.fetch(req, callback=handle_request)
            tornado.ioloop.IOLoop.instance().start()
        else:
            print url, data
            http_client.fetch(req, callback=handle_request_without_ioloop)
        self.redirect('/'+url)
           
class TestHandler(BaseHandler):
    def get(self):
        self.render('website/test.html')

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/test', TestHandler),
            (r'/txt/(.*)', TxtHandler),
            (r"/check_if_name_exists/(.*)", CheckUrlExistHandler),
            (r'/update_contents/(.*)', UpdateContentHandler),
            (r'/change_url/(.*)', ChangeUrlHandler),
            (r'/encrypt_url/(.*)', AddPwdHandler),
            (r"/sina_oauth", SinaOAuthHandler),
            (r"/delete", DeleteHandler),
            (r"/history", HistoryHandler),
            (r"/account/login", AuthLoginHandler),
            (r"/account/logout", AuthLogoutHandler),
            (r"/wblogin_check", WeiboLoginCheckHandler),
            (r"/sina-logout", WeiboLogOutCheckHandler),
            (r"/upload_to_weibo/(.*)", UploadWeiboHandler),
            (r'/(.*)', MainHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            #xsrf_cookies=True,
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            session_secret="my password",
            session_dir="sessions",
        )

        tornado.web.Application.__init__(self, handlers, **settings)
        self.session_manager = common.session.TornadoSessionManager(settings["session_secret"],
            settings["session_dir"])


def main(port):
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(port)
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.instance().start()



if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main(8888)
