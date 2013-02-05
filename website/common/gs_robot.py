#coding=utf8
import sys
import pprint
sys.path.append('../')

import struct
import common.xml2dict

"""
[[{u'count': u'SESSION_KEY_LEN', u'name': u'SessionKey', u'type': u'string'},
  {u'name': u'UserId', u'type': u'dword'},
  {u'name': u'TableId', u'type': u'int'},
  {u'name': u'major', u'type': u'int'},
  {u'name': u'minor', u'type': u'int'},
  {u'name': u'revision', u'type': u'int'}],
"""
def pack_msg_dict(msg):
	for i in msg:
		pass


proto_dict = common.xml2dict.dict_from_xml(open('../config/BnFGameProto.xml').read())
#pprint.pprint(proto_dict)

#proto_dict.keys() = [u'version', u'messages', u'name', u'types', u'defines']

action_list = [2000, 2001]

id2msgname = {}
for i in proto_dict['messages'][0]['message']:
	id2msgname[i['id']] = i['type']

message_name_list = [id2msgname[str(i)] for i in action_list]

#print message_name_list

name2msg = {}
for i in proto_dict['types'][0]['type']:
	name2msg[i['name']] = i['item']


#print name2msg.keys()
msgs = [name2msg[i] for i in message_name_list]


pprint.pprint(msgs)

