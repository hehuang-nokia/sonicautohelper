from nokia.util import *


args = share.gb_args


consip = share.gb_config['console_ip']
consp = share.gb_config['console_port']
dupip = share.gb_config['dut_ip']

if "con" in args:
    f = M0(consip, port=consp)
else:
    f = M0(dupip)

f.sne("show version")

f.hijack()