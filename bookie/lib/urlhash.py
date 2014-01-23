"""Urls are hashed with a sha256 string"""
import hashlib


def generate_hash(url_string):
    m = hashlib.sha256()
    m.update(url_string.encode('utf-8'))
    return unicode(m.hexdigest()[:14])
