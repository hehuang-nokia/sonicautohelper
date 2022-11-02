from nokia.util import *


args = share.gb_args

try:
    consip = share.gb_config['console_ip']
    dutip = share.gb_config['dut_ip']
    consp = share.gb_config['console_port']
except:
    pass

if 'pswd' in share.gb_config:
    pswd = share.gb_config['pswd']
else:
    pswd = None

if 'proxy' in share.gb_config:
    proxy = share.gb_config['proxy']
else:
    proxy = None

if "con" in args:
    f = M0(ip_str=consip, passwd=pswd, port=consp, proxy=proxy)
else:
    f = M0(dutip, passwd=pswd)

f.sne("show version")

ws = share.gb_config['ws_arm32']

f.hijack()