#coding=utf8
import datetime
import tornado.web
import tornado.httpserver
import tornado.httpclient
import tornado.gen

import json
import base64

import os
import re

from urlparse import urljoin
#from config.web_config import PLATFORM


import session
from httputil import iri_to_uri

#from config.web_config import PLATFORM

absolute_http_url_re = re.compile(r"^https?://", re.I)
INTERNAL_IP_PATTERN = re.compile('127.0.0.1|192.168.*.*')



class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def __init__(self, *argc, **argkw):
        super(BaseHandler, self).__init__(*argc, **argkw)
        self.path = ''
#        self.session = session.TornadoSession(self.application.session_manager, self)


        # debug
        #with open('/tmp/http_body', 'a') as f:
        #    f.write('body:'+ self.request.body)
        #    f.write(' url:'+ self.request.uri)
        #    f.write(' timestamp:'+str(datetime.datetime.now()))
        #    f.write('\n')


    # platform apis, support sina, renren, douban
    def get_current_user(self):
        user_id = self.get_cookie('user')
        if user_id:return user_id
#        if (not self.get_cookie('aid')):
#            if not self.session.get('me'):
#                print 'not login...current user'
#                return None
#            aid = self.session.get('me').id
#            sid = self.session.session_id
#            self.set_cookie('aid', str(aid))
#            return self.session.get('username')
#        if self.session.get('me'):
#            return self.session.get('username')
#        else:
#            return None
        #return self.get_cookie('player_name', '')

    def get_current_userid(self):
        if self.get_cookie('S'):
            userid = base64.b64decode(self.get_cookie('S')).split('@@@')[0]
            return userid if userid else None
        else:return None

    def get_host(self):
        """Returns the HTTP host using the environment or request headers."""
        return self.request.headers.get('Host')

    def build_absolute_uri(self, location=None):
        """
        Builds an absolute URI from the location and the variables available in
        this request. If no location is specified, the absolute URI is built on
        ``request.get_full_path()``.
        """
        if not location:
            location = ''
        if not absolute_http_url_re.match(location):
            current_uri = '%s://%s%s' % (self.is_secure() and 'https' or 'http',
                                         self.get_host(), self.path)
            location = urljoin(current_uri, location)
        return iri_to_uri(location)

    def is_secure(self):
        return os.environ.get("HTTPS") == "on"

    def get_error_html(self, status_code, exception=None, **kwargs):
        return self.render_string('_error.htm', status_code=status_code, exception=exception, **kwargs)


class ReqMixin(object):
    user_callback = {}

    def wait_for_request(self, callback):
        cls = ReqMixin
        cls.user_callback.update({self.get_user_id():callback})

    def new_req(self, req):
        cls = ReqMixin
        callback = cls.user_callback[self.get_user_id()]
        callback(req)

class ProxyHandler(BaseHandler, ReqMixin):
    @tornado.web.asynchronous
    def get(self, action):
        if action == 'update':
            self.wait_for_request(self.async_callback(self.send))

        elif action == 'request':
            http = tornado.httpclient.AsyncHTTPClient()
            http.fetch(self.get_argument('url'), callback=self.new_req)
            self.finish()


    def send(self, response):
        # Closed client connection
        if response.error:
            raise tornado.web.HTTPError(500)
        self.write(response.body)
        self.flush()

class DataCombineHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        http_client = tornado.httpclient.AsyncHTTPClient()
        response1 = response2 = response3 = response4 = response5 = response6 = response7 = response8 = response9 = response10 = None
        req1 = self.get_argument('req1', None)
        req2 = self.get_argument('req2', None)
        req3 = self.get_argument('req3', None)
        req4 = self.get_argument('req4', None)
        req5 = self.get_argument('req5', None)
        req6 = self.get_argument('req6', None)
        req7 = self.get_argument('req7', None)
        req8 = self.get_argument('req8', None)
        req9 = self.get_argument('req9', None)
        req10 = self.get_argument('req10', None)
        if req1:response1 = yield tornado.gen.Task(http_client.fetch, req1)
        if req2:response2 = yield tornado.gen.Task(http_client.fetch, req2)
        if req3:response3 = yield tornado.gen.Task(http_client.fetch, req3)
        if req4:response4 = yield tornado.gen.Task(http_client.fetch, req4)
        if req5:response5 = yield tornado.gen.Task(http_client.fetch, req5)
        if req6:response6 = yield tornado.gen.Task(http_client.fetch, req6)
        if req7:response7 = yield tornado.gen.Task(http_client.fetch, req7)
        if req8:response8 = yield tornado.gen.Task(http_client.fetch, req8)
        if req9:response9 = yield tornado.gen.Task(http_client.fetch, req9)
        if req10:response10 = yield tornado.gen.Task(http_client.fetch, req10)
        response_dict = dict()
        if response1:response_dict['req1'] = json.loads(response1.body)
        if response2:response_dict['req2'] = json.loads(response2.body)
        if response3:response_dict['req3'] = json.loads(response3.body)
        if response4:response_dict['req4'] = json.loads(response4.body)
        if response5:response_dict['req5'] = json.loads(response5.body)
        if response6:response_dict['req6'] = json.loads(response6.body)
        if response7:response_dict['req7'] = json.loads(response7.body)
        if response8:response_dict['req8'] = json.loads(response8.body)
        if response9:response_dict['req9'] = json.loads(response9.body)
        if response10:response_dict['req10'] = json.loads(response10.body)
        self.finish(response_dict)
