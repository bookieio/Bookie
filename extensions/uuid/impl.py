#!/usr/bin/python2.7

from hashlib import md5
import uuid

name = "agoogle"
namespace = uuid.NAMESPACE_URL

class Dummy:
    bytes = ""

def python_impl():
    return uuid.uuid3(Dummy(), name).int

def manual_impl():
    #md5hash = md5(namespace.bytes + name).digest()
    md5hash = md5("" + name).digest()
    md5hash = md5hash[:16]
    uu = long(("%02x"*16) % tuple(map(ord, md5hash)), 16)
    #print(uu)
    uu &= ~(0xc000 << 48L)
    #print((uu))
    uu |= 0x8000 << 48L
    #print((uu))
    uu &= ~(0xf000 << 64L)
    #print((uu))
    uu |= 3 << 76L # version 3
    #print((uu))
    return uu

print(python_impl())
print(manual_impl())


