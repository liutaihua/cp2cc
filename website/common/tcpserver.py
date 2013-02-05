#coding=utf8

import re
import json
import time
import socket

import common.util
from gamelogic.profile.profile_controller import ProfileHandler
from gamelogic.equipment.equipment_controller import EquipmentHandler
from gamelogic.package.package_controller import PackageHandler
from gamelogic.skill.skill_controller import SkillHandler
from gamelogic.task.task_controller import TaskHandler
from gamelogic.achive.achive_controller import AchiveHandler

from tornado.netutil import TCPServer
from tornado.util import b

INTERNAL_IP_PATTERN = re.compile('127.0.0.1|192.168.*.*')

handlers = {
    'profile.kill_monster':ProfileHandler,
    'equipment.equip':EquipmentHandler,
    'equipment.unequip':EquipmentHandler,
    'package.pickup':PackageHandler,
    'package.drop':PackageHandler,
    'skill.add_point':SkillHandler,
    }

class HadesServer(TCPServer):
    """TCP server for handling incoming connections from players"""

    def handle_stream(self, stream, address):
        # only accept tcp connection from game server
        if not INTERNAL_IP_PATTERN.match(address[0]):
            stream.close()
        else:
            self.stream = stream
            self.stream.set_close_callback(self._on_disconnect)
            self.wait()

    def _on_disconnect(self, *args, **kwargs):
        pass

    def wait(self):
        """Read from stream until the next signed end of line"""
        self.stream.read_until(b("\n"), self._on_read)

    def _on_read(self, line):
        """Called when new line received from connection"""
        msg = json.loads(line)
        cmd = msg['cmd']
        handler = handlers[cmd]
        result = handler.process_stream(msg, self.db)
        self.stream.write(result)
        self.wait()
