from nokia.util import *


args = share.gb_args


consip = share.gb_config['console_ip']
consp = share.gb_config['console_port']
dupip = share.gb_config['dut_ip']

if 'pswd' in share.gb_config:
    pswd = share.gb_config['pswd']
else:
    pswd = None

if "con" in args:
    f = M0(consip, passwd=pswd, port=consp)
else:
    f = M0(dupip)

f.sne("show version")

ws = share.gb_config['ws_arm32']

f.hijack()