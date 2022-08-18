import sys
import inspect
import traceback
import time
from collections import namedtuple
from operator import itemgetter

from logger import MSG
import share

if __name__ == "__main__":
    def step1():
        pass
    def step2():
        pass


    class testcase(object):
        aaaaaaaaaa = 1
        def __init__(self):
            pass
        def subcase(self): pass

    current_module = sys.modules[__name__]
    all_functions = inspect.getmembers(current_module, inspect.isfunction)
    print all_functions
    print ""


    all_class = inspect.getmembers(current_module, inspect.isclass)
    print all_class
    print ""

    all_membors = inspect.getmembers(testcase, inspect.ismethod)
    print all_membors
    print ""

    print testcase.__dict__
    print ""

    aaa = __import__("device")

    all_membors = inspect.getmembers(aaa, inspect.isclass)
    print all_membors
    print ""

    print sys.modules["share"]

    #print all_functions[0][0]

class TestCase(object):

    def __init__(self, testname="", desc="", build=True):
        self.testname = testname
        self.desc = desc
        self.step_list =[]

        self.userinfo = ""
        self.test_result = []
        self.rv = False
        share.gb_module_name = sys.modules[self.__module__]
        if build:
            self.build()

    def __call__(self):
        return self.rv

    def record_result(self, step=(), result="", duration=0, extra_info = ""):
        desc= step.desc
        TestResult = namedtuple("TestResult", "step mustpass desc result duration info")
        tr = TestResult(step.name, str(step.isrequire), desc, result, duration, extra_info)
        self.test_result.append(tr)

    def record_result_global(self, duration=0):
        x = self.test_result
        totr = "PASS"
        #tott = 0.0
        for oner in x:
            #tott += oner.duration
            if oner.result != "PASS":
                totr = "FAIL"
        self.rv = (totr == "PASS")
        TestResultgb = namedtuple("TestResult", "name desc result duration")
        tr = TestResultgb(self.testname, self.desc, totr, duration)

        share.gb_test_result_brief.append(tr)

    @staticmethod
    def _prt_tbl(tbl_header, test_result):
        fail_idx_ls = []
        warning_idx_ls = []
        for oner in test_result:
            if oner.result != "PASS":
                if oner.result == "FAIL":
                    fail_idx_ls.append(test_result.index(oner) + 1)
                else:
                    warning_idx_ls.append(test_result.index(oner) + 1)

        MSG.printTable(tbl_header + test_result,
                       fail_idx_ls=fail_idx_ls, warning_idx_ls=warning_idx_ls)

    @staticmethod
    def show_result_gb():
        x = share.gb_test_result_brief
        tbl_header = [("Test Case", "Description", "Result", "Duration")]
        MSG.warning("\nSummary:")
        TestCase._prt_tbl(tbl_header, x)


    def show_result(self):
        #for test_r in self.test_result:
            #print test_r
        x = self.test_result
        tbl_header = [('Case "'+self.testname+'"', "Must pass" ,"Description" ,"Result", "Duration", "Info")]
        TestCase._prt_tbl(tbl_header, x)

    def build(self):

        MSG.okblue("\nTest name: " + self.testname)

        all_class = inspect.getmembers(self, inspect.ismethod)

        #print all_class[0][0]  #todo this is the function name !

        for oneclass in all_class:
            if oneclass[0].startswith("step"):
                tmp = inspect.getargspec(oneclass[1]).args

                #todo: use more named tuple
                if "require" in tmp:
                    idx = tmp.index("require")
                    if inspect.getargspec(oneclass[1]).defaults[idx-1]:
                        req_flag=True
                    else:
                        req_flag = False
                #oneclass[1]()
                desc = ""
                if "desc" in tmp:
                    idx = tmp.index("desc")
                    desc = inspect.getargspec(oneclass[1]).defaults[idx-1]

                #self.step_list.append((oneclass[0], oneclass[1]))
                try:
                    #bad naming ???
                    TestStep = namedtuple("TestStep", "name func_p num isrequire desc")
                    ts = TestStep(oneclass[0], oneclass[1],int(oneclass[0].replace("step_","")), req_flag, desc)
                    self.step_list.append(ts)
                except:
                    pass

        self.step_list.sort(key=lambda step: int(step[0].replace("step_","")))
        #alternative way: self.step_list.sort(key=itemgetter(2))
        MSG.okblue("Test is ready to run\n")



    # def add(self, step_number, func):
    #     self.step_list.insert(step_number, func)

    def check(self):
        MSG.okblue("Going to run:")
        for step in self.step_list:
            if step.isrequire:
                MSG.okgreen( step.name + ': "' + step.desc +'" ' + "<required>")
            else:
                MSG.okgreen( step.name + ': ' + step.desc)
        MSG.okblue("\nEnd\n")

    def build_and_check(self):
        self.build()
        self.check()


    def add_info(self,str):
        self.userinfo = str
        if len(self.userinfo) > 32:
            self.userinfo = self.userinfo[:32]

    def clear_user_info(self):
        self.userinfo = ""

    def get_current_user_info(self):
        return self.userinfo

    def run(self, debug=False):
        MSG.warning("Test starts!\n")
        skip_all = False
        startt = 0
        tot_startt=time.time()
        for step in self.step_list:
            #if step[3]:
                #todo: handle this !!
                #print "require run " + step[0]

            if skip_all:
                self.record_result(step, "SKIP")
                continue
            try:
                self.clear_user_info()

                MSG.okgreen("\nRunning " +step.name+"..."+step.desc)

                startt=time.time()
                step.func_p()
                endt=time.time()
                self.record_result(step, "PASS", round(endt-startt,2), self.get_current_user_info())
            except AssertionError as e:
                extra_info = e.message
                _, _, tb = sys.exc_info()
                #traceback.print_tb(tb) # Fixed format
                tb_info = traceback.extract_tb(tb)
                filename, line, func, text = tb_info[-1]
                MSG.fail('\nAssertion failed:')
                MSG.warning('{}\n{}: {}\nLine number: {}\n'.format(text, filename, func, line))
                endt = time.time()
                self.record_result(step, "FAIL", round(endt-startt,2), extra_info)
                if step.isrequire:
                    MSG.fail("Required step failed")
                    skip_all = True
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                _, _, tb = sys.exc_info()
                # traceback.print_tb(tb) # Fixed format
                tb_info = traceback.extract_tb(tb)
                filename, line, func, text = tb_info[-1]
                er = "Unexpected error: " + str(sys.exc_info()[1])
                MSG.warning('\nError:\n{} ({})\nFile {}: {}\nLine number: {}'.format(text, er, filename, func, line))
                endt = time.time()
                self.record_result(step, "ERROR", round(endt-startt,2))
                if step.isrequire:
                    MSG.fail("Required step got errors")
                    skip_all = True
            if debug and not skip_all:
                raw_input(MSG.getwarning("\nPress Enter to continue..."))
                #exit(1)
        tot_endt = time.time()
        self.record_result_global(round(tot_endt-tot_startt,2))
        return self.rv