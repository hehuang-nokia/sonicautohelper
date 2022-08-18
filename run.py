#!/usr/bin/env python

'''
make automation linux box easier..

this app is developed by hhuang
'''

import os
import sys
import threading
import time
import signal
import atexit
import traceback
import code
import re
import getopt
import subprocess
import datetime

source_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(source_dir, "lib"))
sys.path.append(os.path.join(source_dir, "script"))
sys.path.append(os.path.join(source_dir, "script/configuration"))
#globals

class mystdout(object):
    '''
    write immediately to 2 places
    '''
    def __init__(self, stream):
       self.stream = stream
       self.original = sys.stdout
    def write(self, data):
       self.stream.write(data)
       self.original.write(data)
       self.stream.flush()
       self.original.flush()
    def writelines(self, datas):
       self.stream.writelines(datas)
       self.original.writelines(datas)
       self.stream.flush()
       self.original.flush()
    def __getattr__(self, attr):
       return getattr(self.stream, attr)

#todo make this name pid specific so we can have multiple instance
logfile_name = os.path.join(source_dir, "tmp/test.log")
from core import share
if share.gb_logfile_name is None or share.gb_logfile_name == "":
    share.gb_logfile_name = logfile_name
if share.gb_root_dir is None or share.gb_root_dir == "":
    share.gb_root_dir = source_dir

from core.connection import Connection
from core.device import Device
from core.logger import MSG
from lib.display import remove_special_char

#global flags
_flag_goto_interact = True
run_scripts = None
run_only = False
run_show_window_off = False
ini_config = None
section_name = None

def _initLogfiles():
    global run_only
    global run_show_window_off
    os.system("rm -f {}".format(share.gb_logfile_name))
    os.system("touch {}".format(share.gb_logfile_name))

    logpid=os.getpid()
    time_stamp = str(datetime.datetime.now())
    time_stamp = time_stamp[:10] + '_' + time_stamp[11:19]

    #default name
    user_log_file_name = os.path.join(source_dir, "log/log{}_{}.txt".format(logpid,time_stamp))

    user_log_file = open(user_log_file_name, 'w')
    sys.stdout = mystdout(user_log_file)

    if share.gb_terminal_io_logfile_name is None or share.gb_terminal_io_logfile_name == "":
        share.gb_terminal_io_logfile_name = user_log_file_name
    if share.gb_terminal_io_logfile is None:
        share.gb_terminal_io_logfile = user_log_file

    if run_only and run_show_window_off:
        share.gb_logfile = sys.stdout
# open a new x window
# os.system("gnome-terminal -e 'bash -c \"tail -f {}; exec bash\"'".format(logfile_name))
def _openWindow():
    # env = os.environ
    # #workaround for accessibility warning bug
    # env["NO_AT_BRIDGE"] = str(1)
    # #make sure you terminate all background stuff
    # os.system('eval "tmphh() { \\$(which gnome-terminal) \\"\\$@\\" 2>&1 | tr -d \'\\r\' '
    #           '| grep -v \\"GLib-GIO-CRITICAL\\|accessibility bus\\|stop working with a future version\\"; }" ' +
    #           "; trap '' 2 ; tmphh -e 'bash -c \"tail -f {} 2> /dev/null\"' &".format(share.gb_logfile_name))
    # #os.system("gnome-terminal -e 'bash -c \"tail -f {} 2> /dev/null\"' &".format(share.gb_logfile_name))

    os.system(f"python ./lib/display.py {share.gb_logfile_name}")


def display():
    try:
        if share.gb_display is not None:
            if not share.gb_display.is_alive():
                #register a new one
                log_thread = threading.Thread(target=_openWindow)
                log_thread.start()
                share.gb_display = log_thread
            else:
                share.gb_display.start()

            for _ in range(100):
                #print(chr(27) + "[2J"  + "Starting:" + str(_+1)+"%")
                sys.stdout.write('\r' + "Initializing:  " + str(_ + 1) + "%")
                sys.stdout.flush()
                time.sleep(0.05)
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except:
        MSG.warning("Already opened!")

def _commandline_arg():

    global run_scripts
    global run_list
    global run_only
    global run_show_window_off
    global ini_config
    global section_name

    try:
        #todo: edit here for more args
        short_args_option = 'hl:ong:i:s:'
        long_args_option = ['help', 'list', 'onlyrun', 'noshow', 'global', 'ini', 'section']

        #print sys.argv[1:]
        options, remainder = getopt.getopt(sys.argv[1:], short_args_option , long_args_option)
        #print 'OPTIONS   :', options
        for opt, arg in options:
            if opt in ('-h', '--help'):
                raise ValueError("help menu")
            elif opt in ('-l', '--list'):
                run_list = arg
            elif opt in ('-o', '--onlyrun'):
                run_only = True
            elif opt in ('-n', '--noshow'):
                run_show_window_off = True
            elif opt in ('-g', '--global'):
                share.gb_args += arg.split()
                ## changed implementation
            elif opt in ('-i', '--ini'):
                ini_config = arg
            elif opt in ('-s', '--section'):
                section_name = arg

        if remainder:
            run_scripts = [remainder[0]]

            # I dont need this any more..
            if (len(run_scripts) > 1):
                #this happens when there are multiple scripts to run. make sense?
                run_only = True

        try:
            share.gb_scripts = remainder[0]
            share.gb_args = remainder[1:]
        except:
            MSG.okgreen("Running {}.py".format(share._default_script_name))
    except:
        MSG.okblue("\nUsage: -h, --help, -l/--list <list name>, -n/--noshow, -o/--onlyrun\n")
        j = 0
        for i in range(len(long_args_option)):
            MSG.okgreen('--'+long_args_option[i]+':')
            try:
                while short_args_option[j] < 'A' or short_args_option[j] > 'z':
                    j = j + 1
                if '-'+short_args_option[j] in share.explain_args_option[i] :
                    MSG.okblue(share.explain_args_option[i])
                j = j + 1
            except:
                pass

        output = subprocess.check_output("ls script/automation/*py", shell=True)
        outputs = output.split()
        MSG.header("\nAvailable scripts:")
        #todo : add a way to parse the header/description of a script
        for output in outputs:
            output = str(output)
            if "__init__" in output or share._default_script_name in output:
                continue
            MSG.okgreen("\t"+output[2:-1])
        MSG.okblue("example: ./run.py -s mydut autoconfig [arg 1] [arg 2]")

        output = subprocess.check_output("ls script/automation/tests/*py", shell=True)
        outputs = output.split()
        MSG.header("\nAvailable tests:")
        for output in outputs:
            output = str(output)
            if "__init__" in output or share._default_script_name in output:
                continue
            MSG.okgreen("\t" + output[2:-1])
        MSG.okblue("example: ./run.py -s device tests.smoketest")

        sys.exit()

def _prepare_log():
    if share.gb_terminal_io_logfile:
        share.gb_terminal_io_logfile.close()

    if share.gb_logfile:
        share.gb_logfile.close()

        os.system('cat {} >> {}'.format(share.gb_terminal_io_logfile_name, logfile_name))
        #double {

        #os.system("tr -cd '\11\12\15\40-\176' < {} > {}".format(logfile_name, share.gb_terminal_io_logfile_name))

        # os.system('sed - e "s/\r//g" {} > {}'.format(logfile_name,
        #             share.gb_terminal_io_logfile_name))

        os.system('cat {} | sed -r "s/\\x1b\[[0-9;]*m//g" | sed -r "s/\\r//g" | sed -r "s/[[:cntrl:]]\[[0-9]{{1,3}}m//g" > {}'.format(logfile_name,
                    share.gb_terminal_io_logfile_name))
        os.system("dos2unix {} > /dev/null 2>&1".format(share.gb_terminal_io_logfile_name))

        newlines = []
        with open(share.gb_terminal_io_logfile_name, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = remove_special_char(line)
                newlines.append(line)

        with open(share.gb_terminal_io_logfile_name, 'w') as f:
            f.writelines(newlines)

        if share.gb_target_log_name != "":
            os.system("mv {} {}".format(share.gb_terminal_io_logfile_name, share.gb_target_log_name))

def goodbye():
    _prepare_log()
    #print "\nSee you later!"
    _clearall()

def goto_interact():
    global _flag_goto_interact
    if (_flag_goto_interact):
        _flag_goto_interact = False  # dont need this flag anymore.

        # reason to handle here is KeyboardInterrupt works better for getting names in module

        # meaning: handle_sigterm = {signal_handler(signal.SIGINT)} << this whole thing must return a functon with arg (handle_sigterm)
        @signal_handler(signal.SIGINT)
        def handle_sigterm(signum, frame):
            MSG.flatprint("control C sent")
            #goto_interact()
            goodbye()

        code.interact(banner="\n\nVersion = {}\n\nAll libs have been imported\n"
                             "Variables should be localized already\n"
                             "Ctrl-C to exit\n\n\n".format(share.gb_config['version']),
                      local=globals())

def signal_handler(signal_number):
    def __decorator (function ):
        signal.signal(signal_number,function)
        return function
    return __decorator

def _clearall():
    #os.system("rm -f {}".format(logfile_name))
    for dev in share.gb_device_mgr:
        os.killpg(dev.pid, signal.SIGTERM)
    os.killpg(os.getpgid(os.getpid()), signal.SIGTERM)


'''
try:
    fd = Connection()
    fd._telnet("172.16.8.106")
    res = fd._sendandexpect(fd, "adddddddddddfff", "in:")
except:
    e = sys.exc_info()[0]
    #print str(e)
'''

############
#initialize
############

#register for exit func
atexit.register(goodbye)

#parse commandline args
_commandline_arg()

#initialize log files
_initLogfiles()

#load default ini config
from core.configuration import CONFIGMGR
ini_dir = os.path.join(source_dir, "script/configuration/configuration.ini")
configmgr = CONFIGMGR()
if ini_config is not None:
    ini_dir = os.path.join(source_dir, "script/configuration/{}.ini".format(ini_config))

#system config
share.gb_config = configmgr.config_load(ini_dir, share._config_default)

#scripts default
tmp_conf = share.gb_config.copy()
tmp_conf.update(configmgr.config_load_section(ini_dir, "default"))
share.gb_config = tmp_conf
share.gb_module_name = None

#scripts special
if section_name is not None:
    tmp_conf = share.gb_config.copy()
    tmp_conf.update(configmgr.config_load_section(ini_dir, section_name))
    share.gb_config = tmp_conf

try:
    real_name = ""

    log_thread = threading.Thread(target=_openWindow)
    if share.gb_display is None :
        share.gb_display = log_thread
        if not run_show_window_off and __name__ == "__main__":
            display()

            sys.stdout.write ("\n")
            sys.stdout.flush()
    #os.killpg(os.getpgid(os.getpid()),signal.SIGTERM)
    # drop into interactive

    #try:

    #import automation.hitest

    if __name__ == "__main__":
        real_name = __name__
        #copy to local will overwrite __name__

        if run_scripts is None or len(run_scripts) == 0:
            modulename = "automation." + share._default_script_name
            module = __import__(modulename, globals(), locals(), ['*'])
        else:
            for ascript in run_scripts:
                modulename = "automation." + ascript
                #from automation.hitest import *
                module = __import__(modulename, globals(), locals(), ['*'])

        for k in dir(module):
            locals()[k] = getattr(module, k)

    #import automation.hitest as a
    # code start here

# code done here
except KeyboardInterrupt:
    run_only = False
    print ("\n")
    if share.gb_module_name is not None:
        for k in dir(share.gb_module_name):
            locals()[k] = getattr(share.gb_module_name, k)

except ImportError as ie:

    MSG.flatprint (str(ie))
except:
    #e = sys.exc_info()[0]
    #print ("main error = {} \n".format(e))
    traceback.print_exc()

finally:
    pass
    #print "cleaned"
    #_clearall()
"""
example :

y = f.sne("enable")
y = f.sne("show system")

channel_regex = re.compile("((?:\d+:)?(?:\d+/\d+/\d+|\d+/\d+\.\d+))")
res = f.sne("show cable modem fc52.8d5e.a10a verbose | include \"Downstream Channel\"")
'''
'''  CODE !!!!!!!!!


import datetime

while True:
    time.sleep(5)
    y = f.sne("show system")
    print y
    print str(datetime.datetime.now())


"""
if real_name == "__main__" and not run_only:
    #todo  please handle  time out  for  process leak.
    goto_interact()

