import urllib
import urllib2
import time
url = 'http://192.168.0.106:9994/a/message/sys_msg/notify'

for i in range(30):
    req = urllib2.Request(url)
    req.add_data(urllib.urlencode({
        'to_uid':169,'msg':'test %d'%i,'notify_type':2}))
    urllib2.urlopen(req)
