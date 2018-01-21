#!/usr/bin/env python3

import signal
import threading
import readline
from cmd import Cmd
import d2agent


class Shell(Cmd):
    agent = {}
    prompt = "d2agent> "
    intro =         "  _____                                     \n"
    intro = intro + " / ____|                                    \n"
    intro = intro + "| (___  _   _ ___  __ _ _ __   _____      __\n"
    intro = intro + " \\___ \\| | | / __|/ _` | '_ \\ / _ \\ \\ /\\ / /\n"
    intro = intro + " ____) | |_| \\__ \\ (_| | | | | (_) \\ V  V / \n"
    intro = intro + "|_____/ \\__,_|___/\\__,_|_| |_|\\___/ \\_/\\_/  \n"

    def __init__(self, ag):
        self.agent = ag
        Cmd.__init__(self)
    def emptyline(self): pass
    def do_quit(self, arg): self.agent.cmd_quit()
    def do_vnf(self, arg):  self.agent.cmd_vnf(arg)
    def do_nfvi(self, arg): self.agent.cmd_nfvi(arg)
    def do_thrd(self, arg): self.agent.cmd_thrd(arg)
    def do_sys(self, arg):  self.agent.cmd_sys(arg)



def main():
    def cb_sigint(num, frame): pass
    signal.signal(signal.SIGINT, cb_sigint)

    agent = d2agent.d2agent()
    agent.background_d2monitor = background_d2monitor
    agent.nfvi_add('nfvi0', 'labnet5.dpdk.ninja', 8888)
    agent.vnf_add('vnf0', 'nfvi0')
    agent.vnf_add('vnf1', 'nfvi0')
    # agent.vnf_d2mon('vnf0', 'on')

    shell = threading.Thread(target=Shell(agent).cmdloop, name='shell')
    shell.start()



def background_d2monitor(d2vnfobj, agent):
    import time
    import math
    import susanow.d2 as d2
    from d2agent import ts
    from d2agent import cast
    from d2agent import myThread
    assert(isinstance(d2vnfobj , d2agent.d2vnf  ))
    assert(isinstance(agent , d2agent.d2agent))
    ssn_nfvi = d2vnfobj.nfvi.cast2ssn()
    ssn_vnf = ssn_nfvi.get_vnf(d2vnfobj.name)
    if (ssn_vnf == None):
        print('vnf not found')
        return

    seeds = []

    f = open('/tmp/ssn_d2log.log', 'a')
    f.write('[{}] {} start d2 monitoring\n'.format(ts(), ssn_vnf.name()))
    f.flush()

    while True:
        cur_thrd = threading.current_thread()
        cast(myThread, cur_thrd)
        if (cur_thrd.running_flag == False): break

        ssn_vnf.sync()
        n_core = ssn_vnf.n_core()
        rxrate = ssn_vnf.rxrate()
        perf = math.floor(ssn_vnf.perfred() * 100)
        perf = 100 if (perf>100) else perf

        max_rate = 17000000
        if (perf < 90):
            f.write('[{}] {} d2out\n'.format(ts(), ssn_vnf.name()))
            f.flush()
            d2.d2out(ssn_vnf, ssn_nfvi)
        else:
            if (n_core == 1): pass
            elif (n_core == 2):
                if (perf > 85):
                    if (rxrate < (max_rate*0.3)):
                        f.write('[{}] {} d2in pattern2\n'
                                .format(ts(), ssn_vnf.name()))
                        f.flush()
                        d2.d2in(ssn_vnf, ssn_nfvi)
            elif (n_core == 4):
                if (perf > 85):
                    if (rxrate < (max_rate*0.6)):
                        f.write('[{}] {} d2in pattern1\n'
                                .format(ts(), ssn_vnf.name()))
                        f.flush()
                        d2.d2in(ssn_vnf, ssn_nfvi)
        seed = { ssn_vnf.rxrate(), ssn_vnf.perfred(), ssn_vnf.n_core()}
        seeds.append(seed)
        time.sleep(0.5)

    f.write('[{}] finish d2 monitoring\n'.format(ts()))
    f.flush()
    f.close()
    return



if __name__ == '__main__':
    main()



