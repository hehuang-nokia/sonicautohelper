
from core.testbuilder import TestCase


ip = share.gb_config['dut_ip']
pdu_ip = share.gb_config['pdu_ip']
pdu_port = share.gb_config['pdu_port']

ip_standby = share.gb_config['dut_ip_2']

global f

class regcase(TestCase):
    free_cnt = 0

    def step_1(self, require=True, desc="show version demo"):
        global f
        f = Device(ip, "root", "foobar")
        ver = f.sne("show version")

        # ver_parse = ver[ver.index('\n')+1:]
        # self.add_info(ver_parse[25:ver_parse.index('\n')-41])
        f.close()
        #assert "79a1" in ver_parse, "wrong version"

    def step_2(self, require=True, desc="get himem"):
        global f

        f = Device(ip, "root", "foobar")
        f.diag()

        a = f.sne("show module 0 stat himem")
        p = re.search("low water mark       = +(\d+)", a)

        self.free_cnt = p.group(1)

        f.close()

    def step_3(self, require=True, desc="ha"):
        global f

        f = Device(ip, "root", "foobar")

        f.sne("ha module 2 protect")
        f.close()

        time.sleep(3)

        f = Device(ip_standby, "root", "foobar")
        ver = f.sne("show version")
        f.close()

        assert '8' in ver

    def step_4(self, require=False, desc="check hibuf again"):
        global f

        f = Device(ip_standby, "root", "foobar")

        f.wait_cm(need=5,timeout=600)

        qos = f.sne('show cable modem qos')

        print qos

        f.diag()

        a = f.sne("show module 0 stat himem")
        p = re.search("low water mark       = +(\d+)", a)

        reduce = int(self.free_cnt)  -  int(p.group(1))

        print "prt ", self.free_cnt, p.group(1)

        #self.free_cnt = p.group(1)

        f.close()

        assert reduce < 40

    def step_5(self, require=False, desc="change back"):
        global f
        time.sleep(500)
        f = Device(ip_standby, "root", "foobar")

        f.sne("ha module 3 protect")
        f.close()

        time.sleep(30)

        f = Device(ip, "root", "foobar")
        ver = f.sne("show version")
        f.close()

        assert '8' in ver

    def step_6(self, require=False, desc="check hibuf again ag"):
        global f

        f = Device(ip, "root", "foobar")

        qos = f.sne('show cable modem qos')

        print qos


        f.diag()

        a = f.sne("show module 0 stat himem")
        p = re.search("low water mark       = +(\d+)", a)

        reduce = int(self.free_cnt) - int(p.group(1))

        print "prt ", self.free_cnt, p.group(1)

        f.close()

        time.sleep(500)

        assert reduce < 40


#
# tc = regcase(testname="ver2", desc="verr test2")
#
#
# tc.check()
#
# tc.run(debug=True)
# tc.show_result()