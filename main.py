#!/usr/bin/env python3

import signal
import threading
import d2agent
import readline
from cmd import Cmd


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
    agent.nfvi_add('nfvi0', 'labnet5.dpdk.ninja', 8888)
    agent.vnf_add('vnf0', 'nfvi0')
    agent.vnf_add('vnf1', 'nfvi0')
    shell = threading.Thread(target=Shell(agent).cmdloop, name='shell')
    shell.start()


if __name__ == '__main__':
    main()

