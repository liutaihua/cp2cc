import sys
import os
import bz2
import pylibmc
import urllib2
import time
from random import choice



from common.util import get_user_db, get_mc


db = get_user_db()

URL_ENCODE = 'abcdefghijklmnopqrstuvwxyz0123456789'

KV_TXT_SAVE_TIME = "TxtSaveTime:"
KV_TXT = "Txt:"

mc = get_mc(persistence=True)


def handle_request(response):
    if response.error:
        print "Error:", response.error
    else:
        print response.body
    ioloop.IOLoop.instance().stop()

def handle_request_without_ioloop(response):
    if response.error:
        print 'error', response.error
    else:
        print response.body

def get_url_list_by_userid(userid):
    url = []
    url_id_list = db.query('select url_id from user_note where user_id=%d'%int(userid))
    for i in url_id_list:
        id = i['url_id']
        res = db.query('select url from url_info where id=%d'%int(id))
        if res:
            for r in res:
                url.append(r['url'])
    return url
    

def txt_get(id):
    return mc.get(KV_TXT+str(id)) or ''

def txt_set(id, txt):
    txt = txt.rstrip()
    key = KV_TXT+str(id)
    if txt:
        return mc.set(key, txt)
    else:
        mc.delete(key)

def txt_save(url, txt, userid=None):
    id = url_new(url)
    if userid:
        url_id_list = db.query('select url_id from user_note where user_id=%d'%int(userid))
        if url_id_list:
            for url in url_id_list:
                if int(url['url_id']) == id:
                    txt_set(id, txt)
                    return
        db.execute("insert into user_note (url_id, user_id, state, view_time) values(%d, %d, %d, %d)"%(int(id), int(userid), 1, int(time.time())))
        txt_set(id, txt)
    else:
        txt_set(id, txt)

def txt_by_url(url):
    url_id = url_new(url)
    return txt_get(url_id)

def url_random():
    while True:
        url = ''.join(choice(URL_ENCODE) for i in xrange(choice((7,8,9))))
        if not txt_by_url(url):
            break
    return url


def url_by_id(id):
    url = db.execute(
        'select url from url where id=%s',
        id  
    )   
    return url[0] if url else None


def check_if_name_exists(url):
    return True if db.query("select id from url_info where url='%s'"%url) else False

def change_url(id, new_url):
    db.execute("update url_info set url='%s' where id=%d"%(str(new_url), int(id)))

def add_pwd_for_url(url, pwd):
    url_id = url_new(url)
    mc_key = 'PWD:' + str(url_id)
    pwd = hashlib.md5(str(pwd)).hexdigest()
    mc.set(mc_key, pwd)
    return pwd
    

def url_new(url):
    url = str(url.lower())
    id = db.query("select id from url_info where url='%s'"%url)
    if id:
        return id[0]['id']
    else:
        id = db.get('insert into url_info (url) values(%s) returning id', (url,))['id']
        return id

def url_delete(url):
    url_id = url_new(url)
    db.execute('delete from url_info where id=%d'%int(url_id))
    db.execute('delete from user_note where url_id=%d'%int(url_id))
    mc_key = KV_TXT + str(url_id)
    mc.delete(mc_key)

def get_txt_list(user_name):
    url_list = []
    user_id = db.query("select id from account where name='%s'"%user_name)
    if user_id:
        for i in user_id:
            url_id = db.query("select url_id from user_note where user_id='%s'"%i['id'])
