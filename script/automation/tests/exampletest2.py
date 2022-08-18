

from core.testbuilder import TestCase
import time
from core.logger import change_log_name

ip = share.gb_config['dut_ip']
class vertest(TestCase):

    def step_1(self, require=True, desc="load image" ):
        f = Device(ip, "root", "foobar")
        ver = f.sne("show version")
        ver1 = ver[ver.index('\n')+1:]
        self.add_info(ver1[25:ver1.index('\n')-43])
        assert "8.2" in ver1, "wrong version"


    def step_2(self, require=True, desc="ping CM" ):
        f = Device(ip, "root", "foobar")
        ver = f.sne("show version")
        ver1 = ver[ver.index('\n') + 1:]
        a = 1/0
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

