--
Date: 2013-03-07 16:47
Title: "zmq 异步消息队列"
Published: true  
Type: post  
Excerpt:   
--

####zmq  push--pull 方式

**在ZMQ中是淡化服务端和客户端的概念的**:

* 相对的服务端:
* 创建一个SUBer订阅者bind一个端口, 用来接收数据
* 创建一个zmq.PUSH
* 创建一个zmq poller轮询对象,
* 将sub注册到poller, 并赋予zmq.POLLIN意味轮询进来的msg
* 创建sock=poller.poll()开始轮询
* 当有msg发送到suber订阅者的监听端口后, sock.recv()方法将会收到msg,
* 最后使用之前创建的pusher, 使用pusher.send(msg)将消息推送到连接到的puller, 如果无puller, 此msg将被丢弃


**相对的client**:

* 创建zmq.PULL 连接到服务端接收push过来的消息

**消息创建者**:

* 创建一个zmq.PUB对象, 意味着此对象为一个消息发布者: pub = context.socket(zmq.PUB)
* 连接到服务端的suber的监听端口: pub.connect('tcp://%s:%s' % (sub_host, sub_port))
* 最后将需要发送的msg, 使用pub.send(msg)发送给suber订阅者
