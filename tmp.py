#!/usr/bin/env python3


from pprint import pprint
import math, time, threading
import susanow
import susanow.d2 as d2


def main():
    # nfvi0 = susanow.nfvi.nfvi('labnet5.dpdk.ninja', 8888)
    # vnf0  = nfvi0.get_vnf('vnf0')
    # vnf1  = nfvi0.get_vnf('vnf1')
    # if (vnf0 == None or vnf1 == None):
    #     print('vnf get error')
    #     exit(-1)

    background_d2monitor()
    # thrd0 = threading.Thread(
    #         target=background_d2monitor,
    #         args=(vnf0,nfvi0), name='thrd0')
    # thrd0.start()
    # thrd1 = threading.Thread(
    #         target=background_d2monitor,
    #         args=(vnf1,nfvi0), name='thrd1')
    # thrd1.start()
    return

def safe_d2out(vnf, nfvi):
    d2.d2in(ssn_vnf, ssn_nfvi)
    pass # TODO IMplement


def background_d2monitor():
    nfvi0 = susanow.nfvi.nfvi('labnet5.dpdk.ninja', 8888)
    vnf0  = nfvi0.get_vnf('vnf0')
    vnf1  = nfvi0.get_vnf('vnf1')
    if (vnf0 == None or vnf1 == None):
        print('vnf get error')
        exit(-1)

    ssn_vnfs = [vnf0, vnf1]
    ssn_nfvi = nfvi0

    Milion = 1000000
    seeds = []
    d2rules = [
            { 'ncore':2, 'threshold': (17*Milion*0.2) },
            { 'ncore':4, 'threshold': (17*Milion*0.3) },
            { 'ncore':8, 'threshold': (17*Milion*0.6) } ]

    while True:
        for ssn_vnf in ssn_vnfs:
            ssn_vnf.sync()
            name   = ssn_vnf.name()
            n_core = ssn_vnf.n_core()
            rxrate = ssn_vnf.rxrate()
            perf   = ssn_vnf.tpr()
            print('n_core={} perf={}% '.format(n_core, perf), end='')

            if (perf < 90):
                print('{} d2out perf={}'.format(name, perf), end='')
                d2.d2out(ssn_vnf, ssn_nfvi)
            else:
                for rule in d2rules:
                    if (n_core == rule['ncore']):
                        if (perf > 90):
                            if (rxrate < rule['threshold']):
                                print('{} d2in '.format(name), end='')
                                d2.d2in(ssn_vnf, ssn_nfvi)
            print('pps={}M'.format(
                math.floor(rxrate/Milion)))
        time.sleep(0.5)
    return


if __name__ == '__main__':
    main()



