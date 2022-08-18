
import subprocess
import os

g = Device("172.16.8.2", "xx", "xxxxx")
str = g.sne("cat /tftpboot/tes.txt", timeout = 30)
'''
f = Device(share.gb_config["dut_ip"], "xx", "xxx")
f.sne("")
ver = f.sne("show version")
print ver
ver = f.sne("page-off")
print ver
ver = f.sne("show version")
print ver
'''
###############  serious bug !!!

# this can directly run, but need to have the path to run.py

import run

import re
import time


f = Device("172.16.8.82", "xx", "xxx")


f.sne("config")

MSG.warning("gggggg")




'''
# this can directly run, but need to have the path to run.py


import re
import time

ip = share.gb_config['dut_ip']

print share.gb_config['pdu_port']

f = Device(ip, "xx", "xxx")


f.sne("config")

'''


