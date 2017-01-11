#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
utils.py
(c) Will Roberts  11 January, 2017

Utility functions.
'''

import itertools

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)