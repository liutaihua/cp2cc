#coding=utf8

import os


from tornado.options import define, options

FLAVOR = os.environ.get('FLAVOR', 'test')

if FLAVOR == 'prod':
    settings = dict(
            cookie_secret="y+iqu2psQRyVqvC0UQDB+iDnfI5g3E5Yivpm62TDmUU=",
            #login_url="/auth/login",
            debug=False,
            session_secret='terminus',
            session_dir='sessions',
            # template_path=os.path.join(PROJECT_ROOT, "templates"),
            # static_path=os.path.join(PROJECT_ROOT, "static"),
            template_path='templates',
            static_path='static',
            xsrf_cookies=False,
        )

    define('HOST' ,default= 'yyu.me')
    define('DATABASE_ENGINE' ,default= 'postgres')
    define('DATABASE_NAME' ,default= 'test')
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

    define('session_mc', default= ['127.0.0.1:11212'])


DATABASE_ENGINE = options.DATABASE_ENGINE
