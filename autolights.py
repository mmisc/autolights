from phue import Bridge
import yaml
import time

class AutoLight:
    def __init__(self,config):
        yml = yaml.safe_load(open(config, 'r'))
        self.host = yml['host']
        self.interval = yml['interval']
        self.masters = yml['masters']

    def get_state(self, name):
        state = self.bridge.get_light(name)['state']
        return state['on'] & state['reachable']

    def init_masters(self):
        for master in self.masters:
            self.masters[master]['state'] = self.get_state(master)

    def switch(self, slaves, state):
        for s in slaves:
            self.bridge.set_light(s, 'on', state)

    def connect(self):
        self.bridge = Bridge(self.host)
        self.bridge.connect()
        self.bridge.get_api()


    def run(self):
        while True:
            try:
                time.sleep(self.interval)
                self.connect()
                self.init_masters()
                while True:
                    time.sleep(self.interval)
                    for m in self.masters:
                        state = self.get_state(m)
                        master = self.masters[m]
                        if state:
                            if not master['state']:
                                print("Switching on: " + m)
                                self.switch(master['slaves'], True)
                        else:
                            if master['state']:
                                print("Switching off: " + m)
                                self.switch(master['slaves'], False)
                        self.masters[m]['state'] = state

            except Exception as e:
                print(e)

if __name__ == "__main__":
    a = AutoLight('lights.yml')
    a.run()
