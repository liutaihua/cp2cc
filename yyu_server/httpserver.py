#coding=utf8
#system modules:
import time
import sys
import os
os.environ.update({'FLAVOR':'prod'})

#tornado modules:
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.autoreload

import common
import config.web_config

from common.base_httphandler import BaseHandler

from common.auth import AuthLoginHandler, AuthLogoutHandler
from common.sina import SinaOAuthHandler, WeiboLoginCheckHandler, WeiboLogOutCheckHandler

from controller.notepad_controller import TxtHandler, CheckUrlExistHandler, UpdateContentHandler, ChangeUrlHandler, AddPwdHandler, DeleteHandler, HistoryHandler,\
        UploadWeiboHandler, MainHandler

class TestHandler(BaseHandler):
    def get(self):
        self.render('website/test.html')

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/test', TestHandler),
            (r'/txt/(.*)', TxtHandler),
            (r"/check_if_name_exists/(.*)", CheckUrlExistHandler),
            (r'/update_contents/(.*)', UpdateContentHandler),
            (r'/change_url/(.*)', ChangeUrlHandler),
            (r'/encrypt_url/(.*)', AddPwdHandler),
            (r"/sina_oauth", SinaOAuthHandler),
            (r"/delete", DeleteHandler),
            (r"/history", HistoryHandler),
            (r"/account/login", AuthLoginHandler),
            (r"/account/logout", AuthLogoutHandler),
            (r"/wblogin_check", WeiboLoginCheckHandler),
            (r"/sina-logout", WeiboLogOutCheckHandler),
            (r"/upload_to_weibo/(.*)", UploadWeiboHandler),
            (r'/(.*)', MainHandler),
        ]
        tornado.web.Application.__init__(self, handlers, **config.web_config.settings)
        self.session_manager = common.session.TornadoSessionManager(config.web_config.settings["session_secret"],
            config.web_config.settings["session_dir"])
        self.db = common.util.get_user_db()


def main(port):
    tornado.options.parse_command_line()
    print "start on port %s..."%port

    http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
    http_server.listen(port)
    #if int(port) == 9998:
    #    tornado.autoreload.start()
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = tornado.options.options.port
    main(int(port))
