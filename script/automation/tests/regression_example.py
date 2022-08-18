

from core.testbuilder import TestCase


#modulename = "automation." + "defaulttest"
#module = __import__(modulename, globals(), locals(), ['*'])

class testcase(TestCase):

    def dummpy(self, desc="needed, short desc"):
        print "hahahahha dummy"
        pass
    def step_1000(self):
        print "st 2"
        import time
        time.sleep(0.3)
        assert (1 == 2)
        pass
    def step_5000(self, require=True, desc="needed, short desc"):
        print "st 11"
        time.sleep(0.5)
        assert (1 == 2) , "User Fail"

        a = 2/0
        pass
    def step_2000(self):
        time.sleep(0.7)
        print "st 3"

        self.add_info("yes")
        pass

    def step_3000(self,desc="needed, short desc"):
        assert (3==2)
    def step_7000(self):
        assert (3==2)

class testcase2(TestCase):

    def dummpy(self):
        print "additional1"
        pass

class subtest(testcase):
    def step_666(self):
        assert 1==1
        pass

# example: this is how you inherite from test case
at = subtest("fffff")
at.build_and_check()
############
at.run()
# at.show_result()

tc = testcase(testname="ggh", desc="test des")
tcc = testcase2(testname="gghg",build=True)
tc.build()

tc.check()

#tc.add(2,("dummpy",tcc.dummpy, 0, False, ""))
#tc.check()

tc.run()

tc.show_result()
tcc.run()
#tc.show_result()
tcc.show_result()

TestCase.show_result_gb()