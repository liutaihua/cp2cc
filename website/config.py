#coding=utf8

from tornado.options import define, options



define('HOST' ,default= '180.153.136.14:8888')
define('DATABASE_ENGINE' ,default= 'postgres')
define('DATABASE_NAME' ,default= 'note')
define('DATABASE_USER' ,default= 'postgres')
define('DATABASE_PASSWORD' ,default= '')
define('DATABASE_HOST' ,default= 'localhost')
define('DATABASE_PORT' ,default= 3306)
define('DB_COUNT' ,default= 1)

define('MASTER_DB_FLAG' ,default= 1)
define('SLAVE_DB_FLAG' ,default= 2)
define('SERVER_ID' ,default= 1)

define('db_table_dict' ,default= {'account':1, 'profile':1,})


define('mc_list', ['127.0.0.1:11212'])
define('mb_list', ['127.0.0.1:11212'])
define('lock_mc_addr', ['127.0.0.1:11212'])

DATABASE_ENGINE = options.DATABASE_ENGINE
DATABASE_NAME = options.DATABASE_NAME
DATABASE_USER = options.DATABASE_USER
DATABASE_PASSWORD = options.DATABASE_PASSWORD
DATABASE_HOST = options.DATABASE_HOST
DATABASE_PORT = options.DATABASE_PORT
DB_COUNT = options.DB_COUNT
SLAVE_DB_FLAG = options.SLAVE_DB_FLAG
MASTER_DB_FLAG = options.MASTER_DB_FLAG
db_table_dict = options.db_table_dict
SERVERID=1
