import os
import urlparse

import psycopg2

# TODO: Should probably not use this scheme anymore. Need to track down
#       what code actually uses these low-level psycopg2 connections.

try:
    DSN = open(os.path.expanduser("~/.mochiads-dsn")).read().strip()
except IOError:
    DSN = 'user=mochi dbname=mochiads host=db1'
TZ = 'PST8PST8'

def dburi_to_dsn(dburi):
    dsnlst = []
    assert dburi.startswith('postgres://')
    # HACK: This is ugly as hell.
    dburi = 'http' + dburi[len('postgres'):]
    _, host, path, _, _, _ = urlparse.urlparse(dburi)

    user, has_user, rest = host.partition('@')
    if has_user == '@':
        host = rest
        dsnlst.append('user=%s' % (user,))

    rest, has_port, port = host.rpartition(':')
    if has_port == ':':
        host = rest
        dsnlst.append('port=%s' % (port,))

    dsnlst.append('host=%s' % (host,))

    if path:
        dsnlst.append('dbname=%s' % (path.lstrip('/')))

    return ' '.join(dsnlst)

def db_connect(dsn=DSN, tz=TZ, no_isolation=False):
    conn = psycopg2.connect(dsn)
    if no_isolation:
        conn.set_isolation_level(0)
    cur = conn.cursor()
    cur.execute("SET TIMEZONE TO %s", [tz])
    return conn, cur

