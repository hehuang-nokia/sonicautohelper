#!/usr/bin/env python

from pexpect import spawn
from pexpect import pxssh
import re
import os
import time
import sys
try:
    from . import share
    from .logger import MSG
except:
    import share
    from logger import MSG
TTIMEOUT=8
_DEFAULT_PROMPT = re.compile(b"[\S]{2,}[^\r\n]*[>#$][ ]*$", re.MULTILINE)
_DEFAULT_LOGIN = re.compile(b"(?:ogin|sername): ?$", re.MULTILINE)
_DEFAULT_PASSWD = re.compile(b"assword: $", re.MULTILINE)

# source_dir = os.path.dirname(os.path.realpath(__file__)).rstrip("core").rstrip(os.sep).rstrip(
#     "lib").rstrip(os.sep)
# logfile_name = os.path.join(source_dir, "tmp/test.log")

logfile_name = ""
if share.gb_logfile_name != "":
    logfile_name = share.gb_logfile_name
#else
#raise import error
if share.gb_root_dir != "":
    source_dir = share.gb_root_dir
#else
#raise import error

#todo why this not work?
#ff = open(logfile_name, 'w')

from pexpect import searcher_re
from pexpect import EOF
class myspawn(spawn):
    def s_expect(self, pattern, timeout):
        compiled_pattern_list = self.compile_pattern_list(pattern)

        return self.my_expect_loop(searcher_re(compiled_pattern_list), timeout, searchwindowsize=-1)

    def my_expect_loop(self, searcher, timeout = -1, searchwindowsize = -1):

        #todo : this algorithm is not good for searching long output...  smartie pls fix this!!!

        self.searcher = searcher
        if timeout == -1:
            timeout = self.timeout
        if timeout is not None:
            end_time = time.time() + timeout
        if searchwindowsize == -1:
            searchwindowsize = self.searchwindowsize

        try:
            incoming = self.buffer
            freshlen = len(incoming)
            while True: # Keep reading until exception or return.
                index = searcher.search(incoming, freshlen, searchwindowsize)
                if index >= 0:
                    self.buffer = incoming[searcher.end : ]
                    self.before = incoming[ : searcher.start]
                    self.after = incoming[searcher.start : searcher.end]
                    self.match = searcher.match
                    self.match_index = index
                    return self.match_index
                # No match at this point
                if timeout < 0 and timeout is not None:
                    raise TIMEOUT ('Timeout exceeded in expect_any().')
                # Still have time left, so read more data
                c = self.read_nonblocking (self.maxread, timeout)
                freshlen = len(c)
                time.sleep (0.0001)
                incoming = incoming + c
                if timeout is not None:
                    timeout = end_time - time.time()
        except EOF as e:
            self.buffer = ''
            self.before = incoming
            self.after = EOF
            index = searcher.eof_index
            if index >= 0:
                self.match = EOF
                self.match_index = index
                return self.match_index
            else:
                self.match = None
                self.match_index = None
                raise EOF (str(e) + '\n' + str(self))
        except TIMEOUT as e:
            self.buffer = incoming
            self.before = incoming
            self.after = TIMEOUT
            index = searcher.timeout_index
            if index >= 0:
                self.match = TIMEOUT
                self.match_index = index
                return self.match_index
            else:
                self.match = None
                self.match_index = None
                raise TIMEOUT (str(e) + '\n' + str(self))
        except Exception:
            self.before = incoming
            self.after = None
            self.match = None
            self.match_index = None
            raise

class Connection(object):
    last_fd = []
    def __init__(self, log_f=logfile_name):
        self.isssh = False
        self.fd = None
        # for some reason if i open thread, this will not work with 'ff'
        # because thread is after this open !!???

        if (share.gb_logfile != None):
            self.log_f = share.gb_logfile
        else:
            lg = open(log_f, 'wb')
            self.log_f = lg
            share.gb_logfile = lg
        self.ip = None
        self.pid = -1

    def _ssh(self, ip, uname='', pswd=''):
        self.isssh = True
        self.fd = pxssh.pxssh(maxread=99999)
        self.fd.login(ip, uname, pswd)
        self.fd.logfile_read = self.log_f
        self.fd.sendline('bash')
        self._expect(_DEFAULT_PROMPT, timeout=TTIMEOUT)
        #self.fd.prompt()
        self.ip = ip
        self.pid = self.fd.pid
        Connection.last_fd = [self]

    def _telnet(self, ip, port=""):
        #todo move to somewhere  , use root instead

        self.fd = spawn("telnet", args=[ip,port], maxread=99999)
        self.fd.logfile_read = self.log_f

        #self.log_f = ff #if we use ff here
        self.ip = ip
        #print (connection.fd.pid)
        #return self
        self.pid = self.fd.pid
        Connection.last_fd = [self]

    def _send(self,str):

        if str == "CTRL-C":
            self.fd.sendcontrol('c')
        else:
            strr = str.encode("ascii", "ignore")

            #time.sleep(0.001)
            self.fd.sendline(strr)
            time.sleep(0.01)
            #self.log_f.write(strr)
            #self.log_f.flush()
            #print(str.encode("ascii", "ignore"))

    def _expect(self, prompt,timeout=TTIMEOUT):
        try:
            self.fd.expect(prompt, timeout=timeout)
            #print fd.after.decode("ascii", "ignore").replace("\r", "")
            res = (self.fd.before + self.fd.after).decode("ascii", "ignore") #.replace("\r", "")
            #self.log_f.write(res)
            #self.log_f.flush()
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            MSG.fail("TIME OUT?")
            raise ValueError('bad string')
            #res = "TIME OUT !!! CANNOT FIND PROMPT"
        return res

    def _sendandexpect(self, send_str, prompt_str, timeout=TTIMEOUT):
        if (Connection.last_fd[0] != self):
            self.log_f.write("\n                --------- "+str(self.ip)+" ["+str(self.pid)+"] ---------\n")
            Connection.last_fd[0] = self
        self._send(send_str)
        try:
            if self.fd.closed is True or self.fd.terminated is True:
                raise IOError("connection down")

            return self._expect(prompt_str, timeout=timeout)
        except IOError as error:
            raise error
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            e = sys.exc_info()[0]
            MSG.fail("error = {} \n"
                   "sent: {}\n"
                   "get: {}\n"
                   "timeout is {}\n".format(str(e), send_str, self.fd.before, timeout))
            raise ValueError("TIME OUT !!! CANNOT FIND PROMPT")

    def __del__(self):
        if self.fd is not None:
            if self.isssh:
                self.fd.logout()
            else:
                self.fd.close()
        #self.log_f.close()


if __name__ == "__main__":
    logfile_name = "test.log"
    fd = Connection(logfile_name)

    fd._ssh('152.148.150.236',"admin","YourPaSsWoRd")

    #fd._telnet("152.148.146.176", "2010")
    mp = [_DEFAULT_LOGIN, _DEFAULT_PASSWD, _DEFAULT_PROMPT]
    fd._sendandexpect("admin", mp, timeout=1)
    fd._sendandexpect("YourPaSsWoRd", mp)
    try:
        # try:
        #     fd.fd.logfile = fd.log_f.stream
        # except:
        #     fd.fd.logfile = fd.log_f
        # fd.fd.logfile_read = None
        fd.fd.interact(escape_character='^')
    except:
        e = sys.exc_info()[0]
        MSG.fail("hijacking error = {} ".format(e))
    finally:
        fd.fd.logfile = None
        pass

    res = fd._sendandexpect("a", "in:")

    print(res)

    import subprocess
    #open a new x window
    #os.system("gnome-terminal -e 'bash -c \"tail -f {}; exec bash\"'".format(logfile_name))
    os.spawnlp(os.P_NOWAIT, "gnome-terminal -e 'bash -c \"tail -f {}\"'".format(logfile_name))

    #drop into interactive
    import code
    code.interact(local=locals())
