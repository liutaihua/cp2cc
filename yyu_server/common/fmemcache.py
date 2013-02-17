#!/usr/bin/env python
#-*- coding:utf-8 -*-

from pylibmc.pools import ClientPool
from datetime import date, datetime

import pylibmc as memcache

from tornado.options import options


mc_list = options.mc_list
mb_list = options.mb_list

couchbase_client = memcache.Client(mb_list)
couchbase_client.binary = True
couchbase_client.behaviors = {
    "tcp_nodelay": True, "ketama": True
}
#couchbase_pool = ClientPool()
#couchbase_pool.fill(couchbase_client, 20)

memcache_client = memcache.Client(mc_list)
memcache_client.binary = True
memcache_client.behaviors = {
    "tcp_nodelay": True, "ketama": True
}
#memcache_pool = ClientPool()
#memcache_pool.fill(memcache_client, 10)


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
            self.client = couchbase_client
        elif client_type == 'mc':
            self.client = memcache_client
        elif isinstance(client_type, list):
            mc_list = client_type
            self.client = memcache.Client(mc_list)
            self.client.binary = True
            self.client.behaviors = {
                "tcp_nodelay": True, "ketama": True
            }
            

    def set(self, *args):
        args = list(args)
        return self.client.set(*args)

    def get(self, *args):
        return self.client.get(str(args[0]))

    def delete(self, *args):
        return self.client.delete(str(args[0])) != 0

    def add(self, *args):
        args = list(args)
        origin_key = str(args[0])
        args[0] = add_srvid(origin_key)
        return self.client.add(*args) != 0
