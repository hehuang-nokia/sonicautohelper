#from __future__ import print_function #this will also work to create a print function for 2.x
import sys
try:
    from . import share
except:
    import share
import os
import datetime

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class MSG(object):
    @staticmethod
    def warning(content):
        print (bcolors.WARNING + content + bcolors.ENDC)

    @staticmethod
    def fail(content):
        print (bcolors.FAIL + content + bcolors.ENDC)

    @staticmethod
    def header(content):
        print (bcolors.HEADER + content + bcolors.ENDC)

    @staticmethod
    def okgreen(content):
        print (bcolors.OKGREEN + content + bcolors.ENDC)

    @staticmethod
    def okblue(content):
        print (bcolors.OKBLUE + content + bcolors.ENDC)

    @staticmethod
    def flatprint(content):
        print (content)

    @staticmethod
    def getwarning(content):
        return bcolors.WARNING + content + bcolors.ENDC

    @staticmethod
    def getfail(content):
        return bcolors.FAIL + content + bcolors.ENDC

    @staticmethod
    def getheader(content):
        return bcolors.HEADER + content + bcolors.ENDC

    @staticmethod
    def getokgreen(content):
        return bcolors.OKGREEN + content + bcolors.ENDC

    @staticmethod
    def getokblue(content):
        return bcolors.OKBLUE + content + bcolors.ENDC

    @staticmethod
    def logmsg(content):
        if share.gb_logfile:
            try:
                share.gb_logfile.write("\n====== user log =======\n")
                share.gb_logfile.write(content)
                share.gb_logfile.write("\n====== user log =======\n")
                share.gb_logfile.flush()
            except:
                MSG.fail("Failed to log!")


    @staticmethod
    def printTable (tbl, borderHorizontal = '-', borderVertical = '|', borderCross = '+', \
                    ptmethod=lambda x: sys.stdout.write(str(x) + "\n"), fail_idx_ls=[], warning_idx_ls=[]):

        #todo: pass in a list of number of rows so we can change color

        cols = [list(x) for x in zip(*tbl)]
        lengths = [max(map(len, map(str, col))) for col in cols]
        f1 = borderVertical + borderVertical.join(MSG.getokgreen(' {:>%d} ') % l for l in lengths) + borderVertical
        s = borderCross + borderCross.join(borderHorizontal * (l+2) for l in lengths) + borderCross
        f2 = borderVertical + borderVertical.join(MSG.getheader(' {:<%d} ') % l for l in lengths) + borderVertical
        f3 = borderVertical + borderVertical.join(MSG.getfail(' {:>%d} ') % l for l in lengths) + borderVertical
        f4 = borderVertical + borderVertical.join(MSG.getwarning(' {:>%d} ') % l for l in lengths) + borderVertical

        ptmethod("\n")
        ptmethod(s)
        ptmethod(f2.format(*tbl[0]))
        ptmethod(s)

        idx = 1
        for row in tbl[1:]:
            if idx in fail_idx_ls:
                ptmethod(f3.format(*tbl[idx]))
            elif idx in warning_idx_ls:
                ptmethod(f4.format(*tbl[idx]))
            else:
                ptmethod(f1.format(*row))
            ptmethod(s)

            idx += 1


def change_log_name(filename):
    time_stamp = str(datetime.datetime.now())
    time_stamp = time_stamp[:10] + '_' + time_stamp[11:19]
    share.gb_target_log_name = os.path.join(share.gb_root_dir, "log/{}_{}.txt".format(filename,time_stamp))
