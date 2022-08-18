import configparser as ConfigParser
import string
from .logger import MSG

class CONFIGMGR(object):

    """
        TODO  write a spetial load section only F()
        [script1]
        parm2 = 2

        F() should get config[parm2] = 2 instead of config[script1.parm2] = 2
    """
    def config_load_section(self,file, section="default"):
        config = {}
        cp = ConfigParser.ConfigParser()
        cp.read(file)
        for sec in cp.sections():
            name = sec.lower()
            if name == section:
                for opt in cp.options(sec):
                    config[opt.lower()] = cp.get(sec, opt).strip()
        return config

    """
        TODO  write a spetial load section only F()
        [script1]
        parm2 = 2

        F() should get config[parm2] = 2 instead of config[script1.parm2] = 2

    def config_load_section(self,file, section="default"):
        config = {}
        cp = ConfigParser.ConfigParser()
        cp.read(file)
        for sec in cp.sections():
            name = string.lower(sec)
            if name == section:
                for opt in cp.options(sec):
                    config[name + "." + string.lower(opt)] = string.strip(cp.get(sec, opt))
        return config
    """

    def config_load(self,file, config={}):
        """
        returns a dictionary with key's of the form
        <section>.<option> and the values
        """
        config = config.copy()
        cp = ConfigParser.ConfigParser()
        cp.read(file)
        for sec in cp.sections():
            name = sec.lower()
            for opt in cp.options(sec):
                config[name + "." + opt.lower()] = cp.get(sec, opt).strip()
        return config

    def _config_write(self,filename, config):
        """
        given a dictionary with key's of the form 'section.option: value'
        write() generates a list of unique section names
        creates sections based that list
        use config.set to add entries to each section
        """
        try:
            cp = ConfigParser.ConfigParser()
            sections = set([k.split('.')[0] for k in config.keys()])
            map(cp.add_section, sections)
            for k,v in config.items():
                s, o = k.split('.')
                cp.set(s, o, v)
            cp.write(open(filename, "w"))
        except:
            if 'default' in sections:
                MSG.fail('adding default; python bug. "default" raises errors')
            else:
                MSG.fail("Incorrect format. Use <section name>.<variable name>! \n\n"
                         "Example: \nnewconfig = {\n\"myserver.host\": \"1.1.1.1\"\n}")

    def config_write(self, filename, config):
        try:
            parser = ConfigParser.ConfigParser()
            parser.read(filename)
            for key in config:
                key_l = key.split('.')
                parser.set(key_l[0], key_l[1], config[key])
            parser.write(open(filename, "w"))
        except:
            MSG.fail("Incorrect format. Use <section name>.<variable name>! \n\n"
                     "Example: \nnewconfig = {\n\"myserver.host\": \"2.2.2.2\"\n}")
        #self._config_write(filename, self.config_load(filename, config))

    def config_addsection(self, filename, sections):

        cp = ConfigParser.ConfigParser()
        cp.read(filename)
        if sections == 'default':
            cp.set(ConfigParser.DEFAULTSECT, 'var_name', 'var_value')

            ORIG_DEFAULTSECT = ConfigParser.DEFAULTSECT  # <---
            ConfigParser.DEFAULTSECT = 'default'
            try:
                cp.write(open(filename, "w"))
            finally:
                ConfigParser.DEFAULTSECT = ORIG_DEFAULTSECT  # <---
                cpp = ConfigParser.ConfigParser()
                cpp.read(filename)
                cpp.remove_option('default','var_name')
                cpp.write(open(filename, "w"))
            return
        try:
            cp.add_section(sections)
        except:
            pass
        cp.write(open(filename, "w"))

    def config_update(self, filename, newconfig):

        for key in newconfig:
            self.config_addsection(filename, key.split('.')[0])
        self.config_write(filename, newconfig)


if __name__=="__main__":
    # print LoadConfig("/home/hhuang/vob/hhuang_experiment2/script/configuration/82.ini", _config_default)


    #this is how we use config_update()
    newconfig = {
        "default.d": "222",
        "default.dd": "1d11",
        "hhh.dd": "222"
    }
    # from ConfigParser import SafeConfigParser
    #
    # parser = SafeConfigParser()
    # parser.read("/home/hhuang/vob/hhuang_experiment2/script/configuration/test.ini")
    # parser.set('DEFAULT', 'value', '16')
    #
    # # Writing our configuration file to 'example.ini'
    # with open("/home/hhuang/vob/hhuang_experiment2/script/configuration/test.ini", 'wb') as configfile:
    #     parser.write(configfile)

    a =CONFIGMGR()
    #a.config_addsection("/home/hhuang/vob/hhuang_experiment2/script/configuration/test.ini", "default")
    #a.config_write("/home/hhuang/vob/hhuang_experiment2/script/configuration/test.ini", newconfig)
    a.config_update("/home/hhuang/vob/hhuang_experiment2/script/configuration/82.ini", newconfig)