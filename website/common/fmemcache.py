#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
#sys.path.append('../')
from pylibmc.pools import ClientPool
from datetime import date, datetime

import pylibmc as memcache

import json

from tornado.options import options

serverid = options.SERVER_ID

mc_list = options.mc_list
mb_list = options.mb_list

couchbase_client = memcache.Client(mb_list)
couchbase_client.binary = True
couchbase_client.behaviors = {
        "tcp_nodelay": True, "ketama": True
        }
couchbase_pool = ClientPool()
couchbase_pool.fill(couchbase_client, 20)

memcache_client = memcache.Client(mc_list)
memcache_client.binary = True
memcache_client.behaviors = {
        "tcp_nodelay": True, "ketama": True
        }
memcache_pool = ClientPool()
memcache_pool.fill(memcache_client, 10)

def add_srvid(origin_key):
    """docstring for add_srvid"""
    return str('%s#%s'%(serverid, origin_key))

def myencode(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')
    elif isinstance(obj, date):
        return obj.strftime('%Y-%m-%d')
    else:
        raise TypeError('%r is not JSON serializable' % obj)

class Fmemcache():
    def __init__(self, client_type):
        if client_type == 'mb':
            self.client = couchbase_pool
        elif client_type == 'mc':
            self.client = memcache_pool

    def set(self, *args):
        with self.client.reserve() as client:
            args = list(args)
            mod_key = add_srvid(str(args[0]))
            args[0] = mod_key
            return client.set(*args)

    def get(self, *args):
        with self.client.reserve() as client:
            origin_key = str(args[0])
            mod_key = add_srvid(origin_key)
            # 为了兼容原来的数据
            return client.get(origin_key) if client.get(mod_key) == None else client.get(mod_key)

    def delete(self, *args):
        with self.client.reserve() as client:
            origin_key = str(args[0])
            mod_key = add_srvid(origin_key)
            return client.delete(mod_key) != 0

    def delete_multi(self, *args):
        with self.client.reserve() as client:
            args = list(args)
            origin_keys = args[0]
            origin_keys = [add_srvid(i) for i in origin_keys]
            args[0] = origin_keys
            return client.delete_multi(*args) != 0

    def add(self, *args):
        with self.client.reserve() as client:
            args = list(args)
            origin_key = str(args[0])
            args[0] = add_srvid(origin_key)
            return client.add(*args) != 0

    def get_multi(self, *args):
        with self.client.reserve() as client:
            args = list(args)
            origin_keys = args[0]
            origin_keys = [add_srvid(i) for i in origin_keys]
            args[0] = origin_keys
            return client.get_multi(*args)

    def incr(self, *args):
        with self.client.reserve() as client:
            mod_key = add_srvid(str(args[0]))
            return client.incr(mod_key) != 0

    def decr(self, *args):
        with self.client.reserve() as client:
            mod_key = add_srvid(str(args[0]))
            return client.decr(mod_key) != 0
