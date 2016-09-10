"""
A dumb down fortune module that provide single line fortunes.
"""

from random import choice

_fortunes = []

def make_fortune_data_file(fortune_file, *a, **kw):
    with open(fortune_file) as fd:
        _fortunes.extend(s.strip() for s in fd.read().split('%'))

def get_random_fortune(fortune_file):
    return choice(_fortunes)
