"""Urls are hashed with a sha256 string"""
import hashlib


def generate_hash(url_string):
    m = hashlib.sha256()
    m.update(url_string)
    return m.hexdigest()[:14]
