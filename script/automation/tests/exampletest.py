

from core.testbuilder import TestCase
import time
from core.logger import change_log_name

from exampletest2 import vertest
ip = share.gb_config['dut_ip']

change_log_name("vvt")

class testcase(TestCase):

    def step_5(self, require=True, desc="load image" ):
        f = Device(ip, "root", "foobar")
        ver = f.sne("show version")
        ver1 = ver[ver.index('\n')+1:]
        self.add_info(ver1[25:ver1.index('\n')-43])
        assert "8.2" in ver1, "wrong version"


    def step_7(self, require=True, desc="ping CM" ):
        f = Device(ip, "root", "foobar")
        ver = f.sne("show version")
        ver1 = ver[ver.index('\n') + 1:]
        self.add_info(ver1[25:ver1.index('\n') - 43])
        assert "8.4" in ver1, "wrong version"

    def step_3(self, require=False, desc="ping CM2" ):
        f = Device(ip, "root", "foobar")
        ver = f.sne("show version")
        ver1 = ver[ver.index('\n') + 1:]
        self.add_info(ver1[25:ver1.index('\n') - 43])
        assert "8.5" in ver1, "wrong version"


    def step_4(self, require=False, desc="ping CM2" ):
        f = Device(ip, "root", "foobar")
        ver = f.sne("show version")
        ver1 = ver[ver.index('\n') + 1:]
        self.add_info(ver1[25:ver1.index('\n') - 43])
        assert "8.1" in ver1, "wrong version"

    def step_01(self, require=False, desc="ping CM2"):
        tcc = vertest(testname="ver1", desc="verrr test 1")
        if not tcc.run(debug=False):
            print "sub test failed "
        #tcc.show_result()

class tt(testcase):
    def step_2(self, require=True, desc="added" ):
        pass


tc = tt(testname="ver2", desc="verr test2")


tc.check()

tc.run(debug=True)
tc.show_result()

tccc = vertest(testname="verrrrr3", desc="verrr test3")
tccc.run(debug=True)

tccc.show_result()
#tc.run()



TestCase.show_result_gb()