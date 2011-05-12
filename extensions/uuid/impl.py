#!/usr/bin/python2.7

from hashlib import md5
import uuid

name = "google"
namespace = uuid.NAMESPACE_URL

def python_impl():
    return uuid.uuid3(namespace, name).int

def manual_impl():
    md5hash = md5(namespace.bytes + name).digest()
    md5hash = md5hash[:16]
    uu = long(("%02x"*16) % tuple(map(ord, md5hash)), 16)
    uu &= ~(0xc000 << 48L)
    uu |= 0x8000 << 48L
    uu &= ~(0xf000 << 64L)
    uu |= 3 << 76L # version 3
    return uu


print(python_impl())
print(manual_impl())


