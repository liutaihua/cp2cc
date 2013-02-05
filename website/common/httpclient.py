#coding=utf8

#import urllib2
import urllib
import traceback
import random
import tornado.ioloop as ioloop
import json

import tornado.httpclient
http_client = tornado.httpclient.AsyncHTTPClient()

from config.web_config import POSEIDON_HOST, ZEUS_HOST
#POSEIDON_HOST = 'http://192.168.0.106:9994'
#HADES_HOST = 'http://192.168.0.106'



def handle_request(response):
    if response.error:
        print "Error:", response.error
    else:
        print response.body
    ioloop.IOLoop.instance().stop()

def handle_request_without_ioloop( response ):
    if response.error:
        print 'error', response.error
    else:
        print response.body


def broadcast(username, type, msg):
    """
    Arguments:
    - `username`:
    - `type`:
    - `msg`:
    """
    url = POSEIDON_HOST + '/a/message/sys_msg/broadcast'
    data = urllib.urlencode( {
        'username':username,
        'type':type,
        'userid':0,
        'msg':msg,
        })
    req = tornado.httpclient.HTTPRequest(url=url, body=data, method='POST')
    if not ioloop.IOLoop.instance().running():
        http_client.fetch(req, callback=handle_request)
        ioloop.IOLoop.instance().start()
    else:
        http_client.fetch(req, callback=handle_request_without_ioloop)

def system_notify(userid, msg, notify_type):
    url = POSEIDON_HOST + '/a/message/sys_msg/notify'
    data = urllib.urlencode({'to_uid': str(userid), 'msg':json.dumps( msg ), 'userid':0, 'notify_type':notify_type})
    req = tornado.httpclient.HTTPRequest( url=url, method='POST', body=data )
    if not ioloop.IOLoop.instance().running():
        http_client.fetch(req, callback=handle_request)
        ioloop.IOLoop.instance().start()
    else:
        http_client.fetch(req, callback=handle_request_without_ioloop)

def start_server(host, port, map_name, channel, gs_type, rule, camp, permit_uids=0, union_a='0', union_b='0', owner_camp='0'):
    url = ZEUS_HOST + '/start'
    camp = int(camp)
    data = urllib.urlencode(
        dict(host=host,
             port=port,
             mapname=map_name,
             channel=channel,
             gs_type=gs_type,
             rule=rule,
             camp=camp,
             permit_uids=permit_uids,
             union_a=union_a,
             union_b=union_b,
             owner_camp=owner_camp))
    req = tornado.httpclient.HTTPRequest(url = url, method='POST', body=data)
    if not ioloop.IOLoop.instance().running():
        http_client.fetch(req, callback=handle_request)
        ioloop.IOLoop.instance().start()
    else:
        http_client.fetch(req, callback=handle_request_without_ioloop)

def stop_server(mapname, channel):
    url = ZEUS_HOST + '/stop'
    data = urllib.urlencode(
        dict(
            mapname=mapname,
            channel = channel,
            )
        )
    req = tornado.httpclient.HTTPRequest(url=url , method='POST', body=data)
    if not ioloop.IOLoop.instance().running():
        http_client.fetch(req, callback=handle_request)
        ioloop.IOLoop.instance().start()
    else:
        http_client.fetch(req, callback=handle_request_without_ioloop)

def check_pids(host):
    url = ZEUS_HOST + '/check_pids'
    data = urllib.urlencode(
        dict(
            host=host,
            )
        )
    req = tornado.httpclient.HTTPRequest(url=url, method='POST', body=data)
    if not ioloop.IOLoop.instance().running():
        http_client.fetch(req, callback=handle_request)
        ioloop.IOLoop.instance().start()
    else:
        http_client.fetch(req, callback=handle_request_without_ioloop)

#system_notify(1, 1)
