'''
defaults should be put here
impore share to access them
'''

gb = []
gb_device_mgr=[]
gb_logfile= None       #this is fd
gb_logfile_name = ""   #this is the file name
gb_terminal_io_logfile= None       #this is fd
gb_terminal_io_logfile_name = ""   #this is the file name
gb_root_dir = ""
gb_target_log_name = ""
gb_args = []
gb_display = None
gb_scripts = []
gb_config = {} #after loading an ini file, things will be put in this dict shared by everyone
gb_test_result_brief = []
gb_logDisplayPid = None
gb_unbuffer_stdout = None
# this loads first... then ini file

#system wise global...
_config_default = {
    "version": "beta 0.1", #not tagged

    #"default.username": "root",
    #"default.password": "",

}

_default_script_name = "defaultscript"

#cli arguments
explain_args_option = [
    "   -h, help menu",
    "   -l <file>, run a list of scripts",
    "   -o, run and finish. do not enter shell",
    "   -n, do not show the display window",
    "   -g <args as string>, args for scripts",
    "   -i <ini file name>, ini file relative to /script/configuration/",
    "   -s <section name>, section in ini file"
]