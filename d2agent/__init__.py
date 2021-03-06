#!/usr/bin/env python3
import os
import sys
import time
import math
import susanow
import threading



def cmdck(opt, arglen, args):
    if (len(args) == 0): return False
    ret = (args[0]==opt and len(args)>=arglen)
    return ret

def ts():
    from datetime import datetime
    # now = datetime.now().strftime("%s")
    # now = datetime.now().isoformat()
    now = datetime.now().strftime("%H%M%S")
    return now

def cast(ParentalClass, child_object):
    child_object.__class__ = ParentalClass

class myThread(threading.Thread):
    running_flag = True
    def __init__(group=None, target=None, name=None,
            args=(), kwargs={}, *, daemon=None):
        super().__init__( group=None,
            target=target, name=name, args=args)
    def start(self):
        super().start()
        print('start new thread in background tid={}'.format(self.ident))
    def stop(self):
        self.running_flag = False

class d2nfvi:
    name = '<none>'
    addr = '<none>'
    port = 0
    agent = None
    vnfs = []
    def __init__(self, name, addr, port, agent):
        assert(isinstance(agent, d2agent))
        self.name = name
        self.addr = addr
        self.port = int(port)
        self.agent = agent

    def cast2ssn(self):
        nfvi = susanow.nfvi.nfvi(
                host=self.addr,
                port=self.port)
        if (nfvi == None):
            raise Exception('nfvi not found')
        return nfvi

    def add_vnf(self, vnf):
        assert(isinstance(vnf, d2vnf))
        if (vnf.nfvi != None):
            raise Exception('VNF is Already registered to NFVi')
        vnf.nfvi = self
        self.vnfs.append(vnf)

    def del_vnf(self, vnf):
        assert(isinstance(vnf, d2vnf))
        if (vnf.nfvi != self):
            raise Exception('VNF is registered to another NFVi')
        vnf.nfvi = None
        for i in range(len(vnfs)):
            if (vnf == self.vnfs):
                self.vnfs.pop(i)
                return
        raise Exception('VNF is not found')

    def summary(self):
        print('{} (http://{}:{})'.format(self.name, self.addr, self.port))

    def stat(self):
        print('name: {}'.format(self.name))
        print('addr: {}'.format(self.addr))
        print('port: {}'.format(self.port))
        print('n_vnfs: {}'.format(len(self.vnfs)))
        for i in range(len(self.vnfs)):
            print(' - {}: '.format(i), end='')
            self.vnfs[i].summary()


class d2vnf:
    name = '<none>'
    nfvi = None
    agent = None
    def __init__(self, name, nfvi, agent):
        assert(isinstance(agent, d2agent))
        assert(isinstance(nfvi , d2nfvi ))
        self.name = name
        self.agent = agent
        nfvi.add_vnf(self)

    def cast2ssn(self):
        vnf = susanow.nfvi.nfvi(
                host=self.nfvi.addr,
                port=self.nfvi.port).get_vnf(self.name)
        if (vnf == None):
            raise Exception('TSURAI')
        return vnf

    def summary(self):
        print('{} (nfvi:{})'.format(self.name, self.nfvi))

    def stat(self):
        print('name: {}'.format(self.name))
        print('nfvi: {}'.format(self.nfvi))

    def pmon_filename(self):
        return '/tmp/ssn_{}_perfmonitor.csv'.format(self.name)

    def pmon_threadname(self):
        return "{}_perf_mon_to_csv".format(self.name)

    def d2mon_filename(self):
        return '/tmp/ssn_{}_d2monitor.log'.format(self.name)

    def d2mon_threadname(self):
        return '{}_d2monitor'.format(self.name)



class d2agent:
    background_d2monitor=None
    vnfs = []
    nfvis = []
    threads = []
    agent_running = True

    def __init__(self):
        thrd = threading.Thread(
                target=self.jointhraed,
                name="jointhred")
        thrd.start()

    def create_thread_bg(self, name='BGTHREAD', target=None, args=None):
        for i in range(len(self.threads)):
            if (self.threads[i].name == name):
                print('This thread is already running.')
                print('Can\'t duplex thraed.')
                return
        thrd = myThread(
                name=name,
                target=target,
                args=args)
        thrd.start()
        self.threads.append(thrd)

    def jointhraed(self):
        while self.agent_running:
            for i in range(len(self.threads)):
                self.threads[i].join(1)
                if (self.threads[i].is_alive()): continue
                self.threads.pop(i)
                break

    def cmd_quit(self):
        print('DON\'T OVERDO.')
        for i in range(len(self.threads)):
            self.threads[i].stop()
        self.agent_running = False
        sys.exit()
        return

    def cmd_thrd(self, arg):
        usagestr = \
            "Usage: thrd [OPTIONS]\n" \
            "thrd list\n" \
            "thrd destroy <tid>\n"
        args = arg.split()
        if   (cmdck('list'   , 0, args)): self.thrd_list()
        elif (cmdck('destroy', 2, args)): self.thrd_destroy(args[1])
        else: print(usagestr)

    def thrd_destroy(self, tid):
        for i in range(len(self.threads)):
            if (self.threads[i].ident == int(tid)):
                self.threads[i].stop()
                return
        print('thread not found from tid')

    def thrd_list(self):
        for i in range(len(self.threads)):
            print('{}: id={}'.format(
                self.threads[i].name,
                self.threads[i].ident))

    def cmd_vnf(self, arg):
        usagestr = \
            "Usage: vnf [OPTIONS]\n" \
            "vnf list\n" \
            "vnf add <vnf-name> <nfvi-name>\n" \
            "vnf del <vnf-name>\n" \
            "vnf stat <vnf-name>\n" \
            "vnf d2mon <vnf-name> <monitor-sec>\n"
        args = arg.split()
        if   (cmdck('list' , 0, args)): self.vnf_list()
        elif (cmdck('add'  , 3, args)): self.vnf_add(args[1], args[2])
        elif (cmdck('del'  , 2, args)): self.vnf_del(args[1])
        elif (cmdck('stat' , 2, args)): self.vnf_stat(args[1])
        elif (cmdck('d2mon', 3, args)): self.vnf_d2mon(args[1], args[2])
        else: print(usagestr)

    def cmd_sys(self, arg):
        usagestr = \
            "Usage: sys [OPTIONS]\n" \
            "nfvi record <on|off>\n" \
            "nfvi record off\n"
        args = arg.split()
        if (cmdck('record' , 2, args)):
            if (args[1] == 'on'):
                self.create_thread_bg(
                    name='sysrecord_thread',
                    target=background_sysrecord_thread,
                    args=(self,))
            elif (args[1] == 'off'):
                for i in range(len(self.threads)):
                    if (self.threads[i].name == 'sysrecord_thread'):
                        self.threads[i].stop()
                        return
                print('thread is not start yet')
            elif (args[1] == 'clear'):
                f = open('/tmp/ssn_record.csv', 'w')
                f.write('#idx, ts')
                nfvis = self.nfvis
                for nfvi in nfvis:
                    vnfs = nfvi.vnfs
                    for vnf in vnfs:
                        f.write(',{}({}),tpr,ncore'.format(vnf.name, vnf.nfvi.name))
                f.write('\n')
                f.flush()
                f.close()
            else: print(usagestr)
        else: print(usagestr)

    def cmd_nfvi(self, arg):
        usagestr = \
            "Usage: nfvi [OPTIONS]\n" \
            "nfvi add <nfvi-name> <addr> <port>\n" \
            "nfvi del <nfvi-name>\n" \
            "nfvi list\n" \
            "nfvi stat <nfvi-name>\n"
        args = arg.split()
        if   (cmdck('add' , 4, args)):
            self.nfvi_add(args[1], args[2], args[3])
        elif (cmdck('del' , 2, args)): self.nfvi_del(args[1]);
        elif (cmdck('list', 1, args)): self.nfvi_list()
        elif (cmdck('stat', 2, args)): self.nfvi_stat(args[1])
        else: print(usagestr)

    def nfvi_stat(self, nfviname):
        nfvi = self.nfvi_find(nfviname)
        if (nfvi == None):
            print('nfvi not found')
            return
        nfvi.stat()

    def vnf_stat(self, vnfname):
        vnf = self.vnf_find(vnfname)
        if (vnf == None):
            print('vnf not found')
            return
        vnf.stat()

    def vnf_add(self, vnfname, nfviname):
        nfvi = self.nfvi_find(nfviname)
        if (nfvi == None):
            print('nfvi not found')
            return
        vnf = nfvi.cast2ssn().get_vnf(vnfname)
        if (vnf == None):
            print('vnf not found')
            return
        for i in range(len(nfvi.vnfs)):
            if (nfvi.vnfs[i].name == vnfname):
                print('vnf already added')
                return
        vnf = d2vnf(vnfname, nfvi, self)
        self.vnfs.append(vnf)

    def vnf_del(self, vnfname):
        for i in range(len(self.vnfs)):
            if (self.vnfs[i].name == vnfname):
                self.vnfs.pop(i)
                return
        print('vnf not found')

    def vnf_find(self, name):
        for i in range(len(self.vnfs)):
            if (self.vnfs[i].name == name):
                return self.vnfs[i]
        return None

    def nfvi_find(self, name):
        for i in range(len(self.nfvis)):
            if (self.nfvis[i].name == name):
                return self.nfvis[i]
        return None

    def vnf_list(self):
        for i in range(len(self.vnfs)):
            self.vnfs[i].summary()

    def nfvi_add(self, name, addr, port):
        nfvi = d2nfvi(name, addr, port, self)
        self.nfvis.append(nfvi)

    def nfvi_del(self, name):
        for i in range(len(self.nfvis)):
            if (self.nfvis[i].name == name):
                self.nfvis.pop(i)
                return
        print('nfvi not found')

    def nfvi_list(self):
        for i in range(len(self.nfvis)):
            self.nfvis[i].summary()

    def vnf_d2mon(self, vnfname, op):
        vnf = self.vnf_find(vnfname)
        if (vnf == None):
            print('vnf not found')
            return
        assert(isinstance(vnf, d2vnf))
        if (op == 'on'):
            self.create_thread_bg(
                name=vnf.d2mon_threadname(),
                target=self.background_d2monitor,
                args=(vnf, self,))
        elif (op == 'off'):
            for i in range(len(self.threads)):
                if (self.threads[i].name == vnf.d2mon_threadname()):
                    self.threads[i].stop()
                    return
            print('thread is not start yet')
        else: print('syntax is invalid')





def background_sysrecord_thread(agent):
    assert(isinstance(agent , d2agent))
    f = open('/tmp/ssn_record.csv', 'w')

    f.write('#idx, ts')
    nfvis = agent.nfvis
    for nfvi in nfvis:
        vnfs = nfvi.vnfs
        for vnf in vnfs:
            f.write(',{}({}),tpr,ncore'.format(vnf.name, vnf.nfvi.name))
    f.write('\n')
    f.flush()

    i = 0
    while True:
        cur_thrd = threading.current_thread()
        cast(myThread, cur_thrd)
        if (cur_thrd.running_flag == False): break

        ss = '{}, {}'.format(i, ts())
        f.write(ss)
        for nfvi in nfvis:
            vnfs = nfvi.vnfs
            for vnf in vnfs:
                # vnf.summary()
                ssnvnf = vnf.cast2ssn()
                ss = ', {}, {}, {}'.format(
                    ssnvnf.rxrate(),
                    math.floor(ssnvnf.perfred()*100),
                    ssnvnf.n_core())
                f.write(ss)
        f.write('\n')
        f.flush()
        time.sleep(1)
        i = i + 1
    f.close()


