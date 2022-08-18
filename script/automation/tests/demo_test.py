
from core.testbuilder import TestCase
import time
from core.logger import change_log_name

ip = share.gb_config['dut_ip']
#change_log_name("demo_test")  # logfile name is changed from default

global f # Device

class dailytestcase(TestCase):

    def step_1(self, require=True, desc="load image" ): # if require is True, if this step fails, entire script stops
        global f
        f = Device(ip, "root", "foobar")
        ver = f.sne("show version")

        ver_parse = ver[ver.index('\n')+1:]
        self.add_info(ver_parse[25:ver_parse.index('\n')-43])
        assert "8.2" in ver_parse, "wrong version"

    def step_3(self, require=False, desc="show system"):
        syst = f.sne("show system")
        assert "100G" in syst, "wrong card"

class weeklytestcase(dailytestcase):   # derive from testcase

    def step_2(self, require=True, desc="show modem" ):
        scm = f.sne("show cable modem")
        assert "online" in scm, "wrong cm"


'''
you can use things like

    args = share.gb_args

to control which one to run from shell

example:

args = share.gb_args
args.append(' ')

if args[0][0] != "w":

    tc1 = dailytestcase(testname="show version", desc="run daily")
    tc1.run()
    tc1.show_result()
else:
    tc2 = weeklytestcase(testname="show cm", desc="run weekly")
    #tc.check()   # this is helpful for test writers
    #tc.run(debug=True) #DEBUG flag
    tc2.run()
    tc2.show_result()

'''

'''
both will run
'''
tc1 = dailytestcase(testname="show version", desc="run daily")
tc1.run()
tc1.show_result()

tc2 = weeklytestcase(testname="show cm", desc="run weekly")
#tc.check()   # this is helpful for test writers
tc2.run(debug=True) #DEBUG flag
tc2.run()
tc2.show_result()

#tc1.run(debug=True)
#tc1.show_result()

TestCase.show_result_gb()   # if we have tc1, results will show here



