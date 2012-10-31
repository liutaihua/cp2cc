#####创意纯属山寨,仅供笑料, 满足偶尔的性欲

在线随手帖的note,方便命令行下获取一些stdout, 记录它于人分享

#### 安装:
    python setup.py install

使用cp2cc命令记录到在线笔记后, 会返回一个网址, 即使此次笔记的url, url的第2级是随机生成的.
##使用:
#### a, 读取文件内容到在线笔记
    cp2cc < hi.txt

#### b, 通过管道读取:
    cat hi.txt|cp2cc

#### c,手工输入 , 在命令行中输入内容 ; 按 Ctrl + D , 然后回车 , 结束输入
    cp2cc
  ctrl + D

#### d,下载文件
    cp2cc  http://url/xx > 1.txt

#### e, 如果不想使用随机地址, 则自定义地址:
    cp2cc  mynote1 < hi.txt


#### 浏览器浏览
    打开浏览器, 贴入使用cp2cc命令返回的url, 可浏览笔记, 编辑它, 并且会自动保存

