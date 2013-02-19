#coding=utf8
import urllib2
import bz2
from common.base_httphandler import BaseHandler
from tornado.options import options

from common.tools import txt_get, txt_set, txt_save, txt_by_url, url_random, url_new, get_txt_list, get_url_list_by_userid, url_delete, check_if_name_exists, change_url,\
                  add_pwd_for_url, handle_request_without_ioloop, handle_request


HOST = options.HOST

UPLOAD_WEIBO_URL = 'https://api.weibo.com/2/statuses/update.json'

class MainHandler(BaseHandler):
    def get(self, url):
        '''搞一个判断是否从/web_logincheck过来的http referer, 如果是就传个参数给前端, 前端提示一个微薄认证已成功的淡出提示'''
        referer = self.request.headers.get('Referer', None)
        userid = self.get_user_id()
        LOGIN = True if self.get_user_id() else ''
        weibo = True if self.get_cookie('Weibo'+str(userid), None) and referer and LOGIN else ''
        txt = ''
        if url == '':
            self.redirect(url_random())
        else:
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


class CheckUrlExistHandler(BaseHandler):
    def post(self, url):
        res = check_if_name_exists(url)
        res = 'true' if res else 'false'
        return self.finish(res)

class UpdateContentHandler(BaseHandler):
    def get(self, url):
        pass

    def post(self, url):
        userid = self.get_user_id()
        update_content = urllib2.unquote(self.request.body.split('contents=')[1].split('&')[0])
#        id = url_new(url)
        txt_save(url, txt=update_content, userid=userid)
        self.finish(url)

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
        userid = self.get_user_id()
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
            http_client.fetch(req, callback=handle_request_without_ioloop)
        self.redirect('/'+url)
           


class DeleteHandler(BaseHandler):
    def post(self):
        url = self.get_argument('myurl')
        url_delete(url)
        self.redirect('/history')

class HistoryHandler(BaseHandler):
    def get(self):
        userid = self.get_user_id()
        LOGIN = False
        url_list = []
        if userid:
            LOGIN = True
            url_list = get_url_list_by_userid(userid)
        return self.render('website/history.html', url_list=url_list, href="http://myapp.com/", login=LOGIN)
