#!/usr/bin/env python
#-*- coding:utf-8 -*-

import time
import random
import urllib
import socket
import operator

import types
from datetime import date, datetime

# load all config files
import re
import fmemcache
import dbutils
import pgutils

from tornado.options import options

from config.web_config import DATABASE_ENGINE

MAX_DAILY_LIMIT = 60

mc_list = options.mc_list
mb_list = options.mb_list
MASTER_DB_FLAG = 0
SLAVE_DB_FLAG = 1
LOG_MAX_COUNT = 4
SERVER_ID = options.SERVER_ID

def get_mc(persistence):
    """
    获取与memcache的连接
    @return : Fmemcache instance
    """
    mc = fmemcache.Fmemcache('mb') if persistence else fmemcache.Fmemcache('mc')
    mc.binary = True
    mc.behaviors = {
        "tcp_nodelay": True, "ketama": True
    }
    return mc


def get_mc_with_info(mcinfo):
    """
    通过信息获取memcache的连接

    @param list mcinfo : memcache的连接信息

    @return : Fmemcache instance
    """
    return fmemcache.Fmemcache(mcinfo)


def get_user_db(userid=0):
    return get_db_conn_with_info(
        host=options.DATABASE_HOST,
        port=options.DATABASE_PORT,
        username=options.DATABASE_USER,
        pwd=options.DATABASE_PASSWORD,
        dbname=options.DATABASE_NAME
    )


def get_user_db_table(userid, metaname):
    """
    根据玩家的guid获得数据库的正确分表名字

    @param long userid : 玩家的guid
    @param string metaname : 原始的表名

    @return : string
    """
    return metaname


def is_in_same_day(argtime):
    """
    判断argtime和当前时间是否是否在同一天内

    @return : True or False
    """
    now = int(time.time())
    argtime = int(argtime)
    return (argtime / kDaySeconds) == (now / kDaySeconds)
    #return (now-argtime)/kDaySeconds == 0


def get_item(itemid):
    """
    返回道具静态数据

    @type itemid: C{int}
    @param itemid: 道具类型id.

    @return: 道具静态数据的dict,如果没有返回None
    """
    return None


def get_item_info(itemid, attrName, defret=None):
    """
    返回道具静态数据中的某一项

    @type itemid: C{int}
    @param itemid: 道具类型id.

    @type attrName: C{str}
    @param itemid: 想要提取的属性值.

    @type attrName: C{obj}
    @param defret: 如果没有这个属性的话,默认返回值.

    @return: 返回相应的数据,如果没有返回None
    """
    return None


def get_center_db_conn():
    """
    返回中心数据库连接的实例

    @return : instance
    """
    conn = dbutils.Connection(host="%s:%s" % (options.DATABASE_HOST, str(options.DATABASE_PORT)),
        user=options.DATABASE_USER,
        password=options.DATABASE_PASSWORD,
        database=options.DATABASE_NAME)
    return conn


def get_db_conn_with_info(host, port, username, pwd, dbname):
    """
    根据连接信息获得连接的实例
    """
    if DATABASE_ENGINE == 'mysql':
        conn = dbutils.Connection(host="%s:%s" % (host, str(port)), user=username, password=pwd, database=dbname)
    elif DATABASE_ENGINE == 'postgres':
        conn = pgutils.Connection(host='127.0.0.1', database=dbname, user=username, mincached=5)
    return conn



def my_json_decoder(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')
    elif isinstance(obj, date):
        return obj.strftime('%Y-%m-%d')
    else:
        raise TypeError('%r is not JSON serializable' % obj)


class Promise(object):
    pass


def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Returns a bytestring version of 's', encoded as specified in 'encoding'.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if strings_only and isinstance(s, (types.NoneType, int)):
        return s
    if isinstance(s, Promise):
        return unicode(s).encode(encoding, errors)
    elif not isinstance(s, basestring):
        try:
            return str(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return ' '.join([smart_str(arg, encoding, strings_only,
                    errors) for arg in s])
            return unicode(s).encode(encoding, errors)
    elif isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s


def iri_to_uri(iri):
    """
    Convert an Internationalized Resource Identifier (IRI) portion to a URI
    portion that is suitable for inclusion in a URL.

    This is the algorithm from section 3.1 of RFC 3987.  However, since we are
    assuming input is either UTF-8 or unicode already, we can simplify things a
    little from the full method.

    Returns an ASCII string containing the encoded result.
    """
    # The list of safe characters here is constructed from the "reserved" and
    # "unreserved" characters specified in sections 2.2 and 2.3 of RFC 3986:
    #     reserved    = gen-delims / sub-delims
    #     gen-delims  = ":" / "/" / "?" / "#" / "[" / "]" / "@"
    #     sub-delims  = "!" / "$" / "&" / "'" / "(" / ")"
    #                   / "*" / "+" / "," / ";" / "="
    #     unreserved  = ALPHA / DIGIT / "-" / "." / "_" / "~"
    # Of the unreserved characters, urllib.quote already considers all but
    # the ~ safe.
    # The % character is also added to the list of safe characters here, as the
    # end of section 3.1 of RFC 3987 specifically mentions that % must not be
    # converted.
    if iri is None:
        return iri
    return urllib.quote(smart_str(iri), safe="/#%[]=:;$&()+,!?*@'~")


def dict2xml_iter(d):
    for k, v in d.iteritems():
        output = '<%s>' % str(k)
        output += '\n'
        for attr, val in v.items():
            output += '  <%s>' % str(attr)
            output += ' ' + str(val)
            output += '  </%s>' % str(attr)
            output += '  \n'
        output += '</%s>' % str(k)
        yield output


def dict2xml(d):
    return '\n'.join(dict2xml_iter(d))


_long_matches = r'googlebot-mobile|android|avantgo|blackberry|blazer|elaine|hiptop|ip(hone|od)|kindle|midp|mmp|mobile|o2|opera mini|palm( os)?|pda|plucker|pocket|psp|smartphone|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce; (iemobile|ppc)|xiino|maemo|fennec'
_long_matches = re.compile(_long_matches, re.IGNORECASE)
_short_matches = r'1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|e\-|e\/|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(di|rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|xda(\-|2|g)|yas\-|your|zeto|zte\-'
_short_matches = re.compile(_short_matches, re.IGNORECASE)

def is_mobile_browser(user_agent):
    """ Detect mobile browsers by brand name matching.

    This is more reliable way than the user agent database
    to discriminate web and mobile browsers. It is future - proof
    certain brand names are regexp against the user agent string.

    @param user_agent: String, User-agent HTTP header

    @return: True if the browser is mobile.
    """
    if _long_matches.search(user_agent) != None:
        return True

    # SHort matches only peek 4 first chars
    user_agent = user_agent[0:4]
    if _short_matches.search(user_agent) != None:
        return True

    return False

def sort_dict(d, reverse=True):
    ''' proposed in PEP 265, using  the itemgetter '''
    return sorted(d.iteritems(), key=operator.itemgetter(1), reverse=reverse)


def sort_dict_by_key(d, reverse=True):
    return sorted(d.iteritems(), key=operator.itemgetter(0), reverse=reverse)

def sortkeypicker(keynames):
    reverse_tuple = set()
    for i, k in enumerate(keynames):
        if k[:1] == '-':
            keynames[i] = k[1:]
            reverse_tuple.add(k[1:])

    def getit(adict):
        adict = adict[1]
        composite = [adict[k] for k in keynames]
        for i, (k, v) in enumerate(zip(keynames, composite)):
            if k in reverse_tuple:
                composite[i] = -int(v)
        return composite

    return getit


def sort_dict_by_multi_key(d, key_list):
    return sorted(d.iteritems(), key=sortkeypicker(key_list))

