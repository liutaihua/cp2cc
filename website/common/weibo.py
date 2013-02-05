#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '1.01'
__author__ = 'Liao Xuefeng (askxuefeng@gmail.com)'

'''
Python client SDK for sina weibo API v2.

注册微博App后，可以获得app key和app secret，然后定义网站回调地址：

from weibo import APIClient

APP_KEY = '1234567' # app key
APP_SECRET = 'abcdefghijklmn' # app secret
CALLBACK_URL = 'http://www.example.com/callback' # callback url
在网站放置“使用微博账号登录”的链接，当用户点击链接后，引导用户跳转至如下地址：

client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
url = client.get_authorize_url()
# TODO: redirect to url
用户授权后，将跳转至网站回调地址，并附加参数code=abcd1234：

# 获取URL参数code:
code = your.web.framework.request.get('code')
client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
r = client.request_access_token(code)
access_token = r.access_token # 新浪返回的token，类似abc123xyz456
expires_in = r.expires_in # token过期的UNIX时间：http://zh.wikipedia.org/wiki/UNIX%E6%97%B6%E9%97%B4
# TODO: 在此可保存access token
client.set_access_token(access_token, expires_in)
然后，可调用任意API：

print client.get.statuses__user_timeline()
print client.post.statuses__update(status=u'测试OAuth 2.0发微博')
print client.upload.statuses__upload(status=u'测试OAuth 2.0带图片发微博', pic=open('/Users/michael/test.png'))
API调用规则
首先查看新浪微博API文档，例如：

API：statuses/user_timeline

请求格式：GET

请求参数：

source：string，采用OAuth授权方式不需要此参数，其他授权方式为必填参数，数值为应用的AppKey。

access_token：string，采用OAuth授权方式为必填参数，其他授权方式不需要此参数，OAuth授权后获得。

uid：int64，需要查询的用户ID。

screen_name：string，需要查询的用户昵称。

（其它可选参数略）

调用方法：将API的“/”变为“__”，并传入关键字参数，但不包括source和access_token参数：

r = client.get.statuses__user_timeline(uid=123456)
for st in r.statuses:
    print st.text
若为POST调用，则示例代码如下：

r = client.post.statuses__update(status=u'测试OAuth 2.0发微博')
若为上传调用（Multipart Post），传入file-like object参数，示例代码如下：

f = open('/Users/michael/test.png')
r = client.upload.statuses__upload(status=u'测试OAuth 2.0带图片发微博', pic=f)
f.close() # APIClient不会自动关闭文件，需要手动关闭
使用限制
仅支持Web方式调用，不支持口令方式验证。

补充说明
所有API调用均为动态调用，需要根据新浪API文档由HTTP调用方式（GET，POST或POST Multipart）决定APIClient的属性（get，post或upload），方法名（新浪微博API名称替换“/”为“__”），以及关键字参数。

若调用出错，会抛出APIError异常，该异常包含error_code，error和request三个字段，与新浪返回的出错json对应。具体错误原因请查询新浪文档。

若HTTP响应出错（例如404），会抛出urllib2.HTTPError异常。
'''

try:
    import json
except ImportError:
    import simplejson as json
import time
import urllib
import urllib2
import logging

def _obj_hook(pairs):
    '''
    convert json object to python object.
    '''
    o = JsonObject()
    for k, v in pairs.iteritems():
        o[str(k)] = v
    return o

class APIError(StandardError):
    '''
    raise APIError if got failed json message.
    '''
    def __init__(self, error_code, error, request):
        self.error_code = error_code
        self.error = error
        self.request = request
        StandardError.__init__(self, error)

    def __str__(self):
        return 'APIError: %s: %s, request: %s' % (self.error_code, self.error, self.request)

class JsonObject(dict):
    '''
    general json object that can bind any fields.
    '''
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value

def _encode_params(**kw):
    '''
    Encode parameters.
    '''
    args = []
    for k, v in kw.iteritems():
        qv = v.encode('utf-8') if isinstance(v, unicode) else str(v)
        args.append('%s=%s' % (k, urllib.quote(qv)))
    return '&'.join(args)

def _encode_multipart(**kw):
    '''
    A sample multipart/form-data; boundary=ABCD:

--ABCD
Content-Disposition: form-data; name="title"
\r\n
Today
--ABCD
Content-Disposition: form-data; name="1.txt"; filename="C:\1.txt"
Content-Type: text/plain
\r\n
<file content of 1.txt>
--ABCD--
\r\n
    '''
    boundary = '----------%s' % hex(int(time.time() * 1000))
    data = []
    for k, v in kw.iteritems():
        data.append('--%s' % boundary)
        if hasattr(v, 'read'):
            # file-like object:
            ext = ''
            filename = getattr(v, 'name', '')
            n = filename.rfind('.')
            if n != (-1):
                ext = filename[n:].lower()
            content = v.read()
            data.append('Content-Disposition: form-data; name="%s"; filename="hidden"' % k)
            data.append('Content-Length: %d' % len(content))
            data.append('Content-Type: %s\r\n' % _guess_content_type(ext))
            data.append(content)
        else:
            data.append('Content-Disposition: form-data; name="%s"\r\n' % k)
            data.append(v.encode('utf-8') if isinstance(v, unicode) else v)
    data.append('--%s--\r\n' % boundary)
    return '\r\n'.join(data), boundary

_CONTENT_TYPES = { '.png': 'image/png', '.gif': 'image/gif', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.jpe': 'image/jpeg' }

def _guess_content_type(ext):
    return _CONTENT_TYPES.get(ext, 'application/octet-stream')

_HTTP_GET = 0
_HTTP_POST = 1
_HTTP_UPLOAD = 2

def _http_get(url, authorization=None, **kw):
    return _http_call(url, _HTTP_GET, authorization, **kw)

def _http_post(url, authorization=None, **kw):
    return _http_call(url, _HTTP_POST, authorization, **kw)

def _http_upload(url, authorization=None, **kw):
    return _http_call(url, _HTTP_UPLOAD, authorization, **kw)

def _http_call(url, method, authorization, **kw):
    '''
    send an http request and expect to return a json object if no error.
    '''
    params = None
    boundary = None
    if method==_HTTP_UPLOAD:
        params, boundary = _encode_multipart(**kw)
    else:
        params = _encode_params(**kw)
    http_url = '%s?%s' % (url, params) if method==_HTTP_GET else url
    http_body = None if method==_HTTP_GET else params
    req = urllib2.Request(http_url, data=http_body)
    if authorization:
        req.add_header('Authorization', 'OAuth2 %s' % authorization)
    if boundary:
        req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
    resp = urllib2.urlopen(req)
    body = resp.read()
    r = json.loads(body, object_hook=_obj_hook)
    if hasattr(r, 'error_code'):
        raise APIError(r.error_code, getattr(r, 'error', ''), getattr(r, 'request', ''))
    return r

class HttpObject(object):

    def __init__(self, client, method):
        self.client = client
        self.method = method

    def __getattr__(self, attr):
        def wrap(**kw):
            if self.client.is_expires():
                raise APIError('21327', 'expired_token', attr)
            return _http_call('%s%s.json' % (self.client.api_url, attr.replace('__', '/')), self.method, self.client.access_token, **kw)
        return wrap

class APIClient(object):
    '''
    API client using synchronized invocation.
    '''
    def __init__(self, app_key, app_secret, redirect_uri, response_type='code', domain='api.weibo.com', version='2'):
        self.client_id = app_key
        self.client_secret = app_secret
        self.redirect_uri = redirect_uri
        self.response_type = response_type
        self.auth_url = 'https://%s/oauth2/' % domain
        self.api_url = 'https://%s/%s/' % (domain, version)
        self.access_token = None
        self.expires = 0.0
        self.get = HttpObject(self, _HTTP_GET)
        self.post = HttpObject(self, _HTTP_POST)
        self.upload = HttpObject(self, _HTTP_UPLOAD)

    def set_access_token(self, access_token, expires_in):
        self.access_token = str(access_token)
        self.expires = expires_in

    def get_authorize_url(self, display='default'):
        '''
        return the authroize url that should be redirect.
        '''
        return '%s%s?%s' % (self.auth_url, 'authorize', \
                _encode_params(client_id = self.client_id, \
                        response_type = 'code', \
                        display = display, \
                        redirect_uri = self.redirect_uri))

    def request_access_token(self, code):
        r = _http_post('%s%s' % (self.auth_url, 'access_token'), \
                client_id = self.client_id, \
                client_secret = self.client_secret, \
                redirect_uri = self.redirect_uri, \
                code = code, grant_type = 'authorization_code')
        r.expires_in += int(time.time())
        return r

    def is_expires(self):
        return not self.access_token or time.time() > self.expires
