from .connection import Connection
from . import connection
import sys
import re
import time
from . import share
from .logger import MSG

#expect_prompt=[connection._DEFAULT_LOGIN,connection._DEFAULT_PASSWD,connection._DEFAULT_PROMPT]
class Device(object):
    def __init__(self, ip_str, uname=None, passwd=None, port="", usessh=True, prompt=None):
        self.ip = ip_str
        self.pid = -1
        if uname == None or passwd == None:
            MSG.warning ("did not specify uname and passwd")

        if port:
            usessh = False
        self.usessh = usessh
        self.zombie_device = True
        if usessh:
            try:
                self.connection = Connection()
                self.connection._ssh(ip_str, uname, passwd)
                self.mp = connection._DEFAULT_PROMPT
                self.pid = self.connection.pid
                MSG.okgreen("SSH connection succeeded! pid = {}".format(self.pid))
                self.zombie_device = False
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except pxssh.ExceptionPxssh as e:
                MSG.fail("Device ssh Connection Failed! pid={}".format(self.pid))

        else:
            try:
                #bad python... if i just make mp = expect_prmpt..... it is wrong because order matters...
                self.mp = [connection._DEFAULT_LOGIN,connection._DEFAULT_PASSWD,connection._DEFAULT_PROMPT]

                self.connection = Connection()
                self.connection._telnet(ip_str, port)
                self.pid = self.connection.pid

                input_prompt = re.compile(bytes("{}".format(prompt),encoding='utf8'), re.MULTILINE)

                self.mp.append(input_prompt)
                time.sleep(0.5)
                #self.connection._sendandexpect("",self.mp)
                self.connection._sendandexpect(uname, self.mp,timeout=1)
                self.connection._sendandexpect(passwd, self.mp)
                #self.connection._sendandexpect("", self.mp)
                MSG.okgreen("Telnet connection succeeded! pid = {}".format(self.pid))
                self.zombie_device = False
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                if share.gb_config["use_proxy"] == 'yes':
                    MSG.warning("Failed connection. Try proxy")
                    self.connection = Connection()
                    self.connection._telnet(share.gb_config["dhcp_server"], port)
                    self.pid = self.connection.pid
                    # todo: clean this up ?!!!!!!!!!1
                    input_prompt = re.compile(bytes("{}".format(prompt),encoding='utf8'), re.MULTILINE)

                    self.mp.append(input_prompt)
                    time.sleep(0.5)
                    try:
                        # self.connection._sendandexpect("",self.mp)
                        self.connection._sendandexpect(share.gb_config["dhcp_username"], self.mp)
                        self.connection._sendandexpect(share.gb_config["dhcp_password"], self.mp)
                        # self.connection._sendandexpect("", self.mp)
                        res = self.connection._sendandexpect("telnet {}".format(ip_str),self.mp, timeout=30)
                        #todo what is the fail condition
                        if "refuse" in res:
                            return
                        else:
                            self.connection._sendandexpect(uname, self.mp)
                            self.connection._sendandexpect(passwd, self.mp)

                    except ValueError as e:
                        MSG.fail("Device Telnet Connection Failed pid={}".format(self.pid))
                else:
                    MSG.fail("Device Telnet Connection Failed pid={}".format(self.pid))

        if self not in share.gb_device_mgr:
            share.gb_device_mgr.append(self)

    def __del__(self):
        self.connection.__del__()
        if self in share.gb_device_mgr:
            share.gb_device_mgr.remove(self)

    def sne(self, send_str="\n", prompt=None, timeout=connection.TTIMEOUT, sendonly=False):
        if self.zombie_device:
            MSG.fail("There is no usable connection to send")
            return None
        try:
            if sendonly:
                timeout = 1 #send only is not send only... we sometimes need the return...
            if prompt is None:
                pr = self.mp
            else:
                pr = prompt
            return self.connection._sendandexpect(send_str, pr, timeout)

        except IOError as error:
            if str(error) == "connection down":
                MSG.fail("Connection is down (connection). Open a new one!")
                self.__del__()
                return "INVALID OUTPUT"
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            if sendonly == False:
                MSG.fail ("Yes! TIMEOUT!\n")
                MSG.okblue(self.connection.fd.before.decode("ascii", "ignore"))

                if self not in share.gb_device_mgr:
                    MSG.fail("Connection is down (mgr). Open a new one!")
                return self.connection.fd.before.decode("ascii", "ignore")
            else:
                sendonlyres = self.connection.fd.before.decode("ascii", "ignore")
                self.connection._send("\n")
                self.connection._expect("\n")#clear before buffer
                MSG.okgreen("Not really! Check it yourself!")
                return sendonlyres

    def stoplog(self):
        try:
            self.connection.fd.logfile_read = None
        except:
            MSG.fail("stop logging failed: {}".format(e))

    def resumelog(self):
        try:
            self.connection.fd.logfile_read = self.connection.log_f
        except:
            MSG.fail("resuming logging failed: {}".format(e))

    def hijack(self, escape='^'):
        if self.zombie_device:
            MSG.fail("There is no usable connection")
            return None
        MSG.okblue("\nUse the connection here!")
        MSG.warning("Type '^' to escape ")
        try:
            # try:
            #     self.connection.fd.logfile = self.connection.log_f.stream
            # except:
            #     self.connection.fd.logfile = self.connection.log_f
            #self.stoplog()
            if share.gb_unbuffer_stdout:
                sys.stdout = share.gb_unbuffer_stdout
            self.connection.fd.interact(escape_character=escape)
            sys.stdout = share.gb_unbuffer_stdout.original
        except:
            e = sys.exc_info()[0]
            MSG.fail("hijacking error = {} ".format(e))
        finally:
            # self.connection.fd.logfile = None
            #self.resumelog()
            pass

    def close(self):
        self.__del__()

