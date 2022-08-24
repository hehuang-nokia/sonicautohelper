'''this module has to run as a standalone process because of tkinter'''
import sys
import tkinter.ttk as ttk
import tkinter as tk
import tkinter.font
import sys
import re
from core import share
from core.logger import MSG
import threading
import os
import subprocess
import signal
import time
# total = len(sys.argv)

def _openWindow():
    # env = os.environ
    # #workaround for accessibility warning bug
    # env["NO_AT_BRIDGE"] = str(1)
    # #make sure you terminate all background stuff
    # os.system('eval "tmphh() { \\$(which gnome-terminal) \\"\\$@\\" 2>&1 | tr -d \'\\r\' '
    #           '| grep -v \\"GLib-GIO-CRITICAL\\|accessibility bus\\|stop working with a future version\\"; }" ' +
    #           "; trap '' 2 ; tmphh -e 'bash -c \"tail -f {} 2> /dev/null\"' &".format(share.gb_logfile_name))
    # #os.system("gnome-terminal -e 'bash -c \"tail -f {} 2> /dev/null\"' &".format(share.gb_logfile_name))

    #os.system(f"python ./lib/display.py {share.gb_logfile_name}")
    cmd = f"python ./lib/display.py {share.gb_logfile_name}"
    try:
        proc = subprocess.Popen(cmd, shell=True, start_new_session=True)
        share.gb_logDisplayPid = proc.pid
    except (ValueError, subprocess.TimeoutExpired, subprocess.SubprocessError):
        MSG.fail("Failed to open a new window")


def display(on=True):
    if not on:
        if share.gb_logDisplayPid:
            os.killpg(share.gb_logDisplayPid, signal.SIGTERM)
            share.gb_logDisplayPid = None
    else:
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

def remove_special_char(line):
    # todo this is not the best regex
    line = re.sub(r'.*\x07|.*\[K', '', line)# '\a' is '\x07'
    maxcnt = 10
    while '\b' in line and maxcnt > 1:
        maxcnt -= 1
        nline = re.sub('[^\b]\b', '', line, count=1)
        if nline == line:
            line = nline
            break
    line = re.sub('\b', '', line)
    return line

class Textwin(ttk.Frame):
    '''output realtime log'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stopped = False
        self._button = None

    # ensure a consistent GUI size
        self.grid_propagate(False)
    # implement stretchability
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    # create a Text widget
        self.txt = tk.Text(self,height=50, width=100)
        self.txt.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

    # create a Scrollbar and associate it with txt
        scrollb = ttk.Scrollbar(self, command=self.txt.yview)
        scrollb.grid(row=0, column=1, sticky='nsew')
        self.txt['yscrollcommand'] = scrollb.set

    def refresh(self):
        if not self._stopped:
            self.txt.delete('1.0', tk.END)
            with open(lgfilename, 'r', encoding="ISO-8859-1") as f:
                lines = f.readlines()
                for line in lines:
                    line = remove_special_char(line)
                    win.txt.insert(tk.END, line)
            self.txt.see('end')
        self.after(100, self.refresh)

    def toggle_scroll(self):
        self._stopped = not self._stopped
        self._button.configure(text="start" if self._stopped else "stop", bg='green' if self._stopped else 'red')

    def make_button(self):
        self._button = tk.Button(main_window, text="stop", bg='red', width=20, command=self.toggle_scroll)
        self._button['font'] = tk.font.Font(family='Helvetica')
        self._button.pack()

    def make_txt(self):
        self.txt.config(font=("consolas", 12), undo=True, wrap='word')
        self.txt.config(borderwidth=3, relief="sunken")
        self.txt.pack()

if __name__ == "__main__":
    cmdargs = sys.argv  # str(sys.argv)#
    # print("The total numbers of args passed to the script: %d " % total)
    # print("Args list: %s " % cmdargs)
    lgfilename = str(cmdargs[1])
    main_window = tk.Tk()
    win = Textwin(main_window)
    win.pack(fill="both", expand=True)
    win.config(width=600, height=600)
    main_window.title("Output")
    win.make_txt()
    style = ttk.Style()
    style.theme_use('clam')
    win.make_button()
    win.after(100, win.refresh)

    try:
        main_window.mainloop()
    except KeyboardInterrupt:
        sys.exit(0)