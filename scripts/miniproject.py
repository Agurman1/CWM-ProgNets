#!/usr/bin/env python3

import re

from scapy.all import *

class P4calc(Packet):
    name = "P4calc"
    fields_desc = [ StrFixedLenField("P", "P", length=1),
                    StrFixedLenField("Four", "4", length=1),
                    XByteField("version", 0x01),
    		    BitField("action", 0, 1),
                    IntField("quantity", 0),
                    IntField("priceB", 0) ]

#trade_pkt = Ether() / IP() / TradeHeader(action=1, quantity=100, price=50)
#sendp(trade_pkt, iface="eth0")






bind_layers(Ether, P4calc, type=0x1234)

class NumParseError(Exception):
    pass

class OpParseError(Exception):
    pass

class Token:
    def __init__(self,type,value = None):
        self.type = type
        self.value = value

def num_parser(s, i, ts):
    pattern = "^\s*([0-9]+)\s*"
    match = re.match(pattern,s[i:])
    if match:
        ts.append(Token('num', match.group(1)))
        return i + match.end(), ts
    raise NumParseError('Expected number literal.')


def op_parser(s, i, ts):
    pattern = "^\s*([-+&|^])\s*"
    match = re.match(pattern,s[i:])
    if match:
        ts.append(Token('num', match.group(1)))
        return i + match.end(), ts
    raise NumParseError("Expected binary operator '-', '+', '&', '|', or '^'.")


def make_seq(p1, p2):
    def parse(s, i, ts):
        i,ts2 = p1(s,i,ts)
        return p2(s,i,ts2)
    return parse

def get_if():
    ifs=get_if_list()
    iface= "veth0-1" # "h1-eth0"
    #for i in get_if_list():
    #    if "eth0" in i:
    #        iface=i
    #        break;
    #if not iface:
    #    print("Cannot find eth0 interface")
    #    exit(1)
    #print(iface)
    return iface

def main():

    p = make_seq(num_parser, make_seq(op_parser,num_parser))
    s = ''
    #iface = get_if()
    iface = "enx0c37965f8a1b"

    while True:
        s = int(input('> '))
        t = int(input('> '))
        if s == "quit":
            break
        print(s, t)
        if t == "quit":
       	    break
        try:
            in1 = s
            in2 = t
            pkt = Ether(dst='00:04:00:00:00:00', type=0x1234) / P4calc(priceB=in1, quantity=in2)

            pkt = pkt/' '

            #pkt.show()
            resp = srp1(pkt, iface=iface,timeout=5, verbose=False)
            if resp:
                p4calc=resp[P4calc]
                if p4calc:
                    print(p4calc.action)
                else:
                    print("cannot find P4calc header in the packet")
            else:
                print("Didn't receive response")
        except Exception as error:
            print(error)


if __name__ == '__main__':
    main()

