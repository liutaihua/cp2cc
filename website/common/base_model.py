#!/usr/bin/env python
#coding=utf-8

import util
import time
import common.exceptions as exception
import config.membase_config
import config.game_config

class BaseModel(object):
    """
    所有model的基类

    init函数必须在实例化后执行
    """

    """ ATTRIBUTES
    long _userid : 拥有者的guid
    string _mc_key : model操作memcache的key
    obj _mc : memcache对象
    obj _db : 数据库对象
    dict _data : model加载进来的数据
    string _lock_key : 加锁和解锁的时候使用的key
    obj _lock_mc : 加锁和解锁使用的memcache
    """


    def __init__(self, userid):
        """
        初始化函数

        @param long userid : model拥有者的guid

        @return  :
        """

        if self.__class__ is BaseModel:
            raise NotImplementedError(self.__name__)

        self._userid = int(userid)
        self._mc_key = ''
        self._persistence = True
        self._mc = util.get_mc(persistence=self._persistence)
        self._lock_mc = util.get_mc_with_info(config.membase_config.lock_mc_addr)
        #self._db = util.get_user_db(self._userid)
        #self._db = None
        self._server_id = config.game_config.SERVER_ID
        self._lock_key = ''
        self._data = None
        #self.init()

    def init(self):
        """
        model执行初始化函数

        @return : True or False
        """

        self._data = self.load()


        #if self._data is None:
        #    self._data = self.load_from_db()
        #    return self.save()

        return True


    def get_owner(self):
        """
        返回model拥有者的guid

        @return : long
        """

        return self._userid

    def load(self):
        """
        根据_mc_key从memcache加载数据

        @return : dict or None
        """
        return self._mc.get(self._mc_key)

    def save(self):
        """
        存储数据到memcache中

        @return : True or False
        """

        if len(self._mc_key) == 0:
            raise exception.MemcacheError

        if self._data is None:
            raise exception.MemcacheError

        return self._mc.set(self._mc_key, self._data)

    def load_from_db(self):
        """
        从数据库中加载数据
        子类一定要重载

        @return : dict or None
        """

        return None

    def save_to_db(self, idlist):
        """
        根据idlist,存储数据到数据库
        如果某些model不需要idlist的就传入None
        子类一定要重载

        @param list idlist : 要保存到数据库的id列表

        @return : True or False
        """

        return False

    def lock(self):
        """
        加锁

        @return : True or False
        """
        if len(self._lock_key) == 0:
            raise exception.LockError
        if not self._lock_mc.add(self._lock_key, 0, 5):
            time.sleep(0.01)
            if not self._lock_mc.add(self._lock_key, 0, 5):
                time.sleep(0.01)
                if not self._lock_mc.add(self._lock_key, 0, 5):
                    time.sleep(0.01)
                    if not self._lock_mc.add(self._lock_key, 0, 5):
                        return False
        return True
        #return self._lock_mc.add(self._lock_key, 0, 5)

    def unlock(self):
        """
        解锁

        @return : True or False
        """
        if len(self._lock_key) == 0:
            raise exception.LockError

        return self._lock_mc.delete(self._lock_key)

    def is_exist(self):
        """
        判断这个model是不是存在

        @return : True or False
        """

        return self._data is not None

    def up_model(self, upid):
        """
        调用相应model的up_time
        对于不需要upid的model,upid约定传0进来

        @param int upid : 要更新的upid

        @return :
        """

        return

    def flush_mc(self):
        self._mc.delete(self._mc_key)
