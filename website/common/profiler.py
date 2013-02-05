#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
run in command line:
    python system_profile.py 1

the 1 cmd in cmd_list is called 
"""


from process import process_cmd
from test_script import cmd_list
import json


def test(cmd_num):
    process_cmd(json.dumps(cmd_list[cmd_num]), 0, 821784434) 

if __name__ == "__main__":
    import py_ext
    import hotshot
    import hotshot.stats
    import sys
    py_ext.amc()
    py_ext.ssc()
    prof = hotshot.Profile("fm_prof.txt", 1)
    prof.runcall(test, cmd_num=sys.argv[1])
    prof.close()
    p = hotshot.stats.load("fm_prof.txt")
    p.print_stats()
