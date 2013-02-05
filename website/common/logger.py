#coding=utf8
import traceback
import syslog

prod_to_log = {
    'hades':syslog.LOG_LOCAL1,
    'poseidon':syslog.LOG_LOCAL2,
    'zeus':syslog.LOG_LOCAL3,
    'hera':syslog.LOG_LOCAL4,
    'mq':syslog.LOG_LOCAL5,
    'error':syslog.LOG_LOCAL7,
    }

def log(prod, category, value):
    value['category'] = category
    syslog.openlog(prod, syslog.LOG_PID, prod_to_log[prod])
    data = " ".join(["%s=%s"%(k,v) for k, v in value.items()])
    syslog.syslog(data)


def errlog(prod, txt):
    syslog.openlog(prod, prod_to_log['error'])
    syslog.syslog(syslog.LOG_ERR, txt)

def tracelog():
    tb = traceback.format_exc()
    errlog('hades', tb)
