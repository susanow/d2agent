#!/usr/bin/env python3


from pprint import pprint
import math, time, threading
import susanow
import susanow.d2 as d2


def main():
    nfvi0 = susanow.nfvi.nfvi('labnet5.dpdk.ninja', 8888)
    vnf0  = nfvi0.get_vnf('vnf0')
    vnf1  = nfvi0.get_vnf('vnf1')
    if (vnf0 == None or vnf1 == None):
        print('vnf get error')
        exit(-1)

    # background_d2monitor()
    thrd0 = threading.Thread(
            target=background_d2monitor,
            args=(vnf0,nfvi0), name='thrd0')
    thrd0.start()
    thrd1 = threading.Thread(
            target=background_d2monitor,
            args=(vnf1,nfvi0), name='thrd1')
    thrd1.start()
    return


class Safed2:
    def __init__(self):
        self.lock = threading.Lock()
    def d2out(self, ssn_vnf, ssn_nfvi):
        with self.lock:
            d2.d2out(ssn_vnf, ssn_nfvi)
    def d2in(self, ssn_vnf, ssn_nfvi):
        with self.lock:
            d2.d2in(ssn_vnf, ssn_nfvi)

safed2 = Safed2()

def background_d2monitor(ssn_vnf, ssn_nfvi):

    Milion = 1000000
    d2rules = {
        "d2out": 90,
        "d2in" : {
            "promiss": 90,
            "thresholds": [
                { 'ncore':2, 'threshold': (17*Milion*0.22) },
                { 'ncore':4, 'threshold': (17*Milion*0.35) },
                { 'ncore':8, 'threshold': (17*Milion*0.6) }
            ]
        }
    }

    while True:
        ssn_vnf.sync()
        name   = ssn_vnf.name()
        n_core = ssn_vnf.n_core()
        rxrate = ssn_vnf.rxrate()
        perf   = ssn_vnf.tpr()

        if (perf < d2rules["d2out"]):
            print('{} d2out '.format(name))
            safed2.d2out(ssn_vnf, ssn_nfvi)
        else:
            for rule in d2rules['d2in']['thresholds']:
                if (n_core == rule['ncore']):
                    if (perf > d2rules['d2in']['promiss']):
                        if (rxrate < rule['threshold']):
                            print('{} d2in '.format(name))
                            safed2.d2in(ssn_vnf, ssn_nfvi)
        time.sleep(0.25)
    return


if __name__ == '__main__':
    main()



