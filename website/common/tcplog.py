#coding=utf8

import socket
import time



def get_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('127.0.0.1', 4242))
    except socket.error:
        print "cannot connect to log server"
    return sock

    sock.close()

def log(category, value):
    return
    sock = get_socket()
    value["category"] = category
    data = " ".join(["%s=%s"%(k,v) for k, v in value.items()])
    sock.send(data)
    sock.close()

def main():
    cnt = 0
    for i in range(1000):
        cnt += 1
        if cnt % 10 == 0:
            time.sleep(1)

if __name__ == '__main__':
    main()
