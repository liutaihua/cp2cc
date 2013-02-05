import json

import socket
import time
import threading


_local_logger = threading.local()
def get_socket():
    try:
        sock = _local_logger.socket
    except AttributeError:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        _local_logger.socket = sock
    return sock

def get_addr():
    host, port = '192.168.0.106', 1463
    return host, int(port)

# This the the main user facing API for this module.
def log(category, msg=None, addr=None):
    """Sends a UDP log message. Automatically timestamps and tags the
    message with useful information.

    category -- A short string identifying the type of message this
    is. All messages of the same category will end up mixed together in
    the same log files.

    msg -- The message to be logged. Either a string or a
    dictionary. Dictionaries must be JSON safe (no complex objects).

    addr -- Override the UDP address the log is sent to. Typically not
    needed.
    """
    if addr is None:
        addr = get_addr()

    # handle legacy case of only one argument. this can go away once all
    # the callsites are converted.
    if msg is None:
        msg = category
        category = "udplog_unknown"
    if isinstance(msg, unicode) or isinstance(msg, str):
        msg = { 'message': msg }

    if not isinstance(msg, dict):
        raise TypeError("msg must be dict or string")

    msg.update({ 'timestamp': time.time(),
                 'hostname': 'test_hostname',
                 'flavor': 'test_flavor' })
    if not msg.has_key('appname'):
        msg.update({ 'appname': 'test_appname' })

    data = "%s:\t%s" % (category, json.dumps(msg))

    sock = get_socket()
    sock.sendto(data, addr)

def main():
    sock = get_socket()
    sock.bind(get_addr())
    while True:
        data, addr = sock.recvfrom(4096)
        print data.rstrip()

if __name__ == '__main__':
    main()
