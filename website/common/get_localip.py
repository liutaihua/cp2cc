def get_localip():
    from socket import socket, SOCK_DGRAM, AF_INET
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(('8.8.8.8',0))
    ip = s.getsockname()[0]
    s.close()
    return ip
