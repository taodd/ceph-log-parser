#!/usr/bin/python

from __future__ import print_function
import templates.mds.tpl as mdstpl
import common.utils as utils

def word2idx(line):
    words = line.strip().split()
    print(words)
    words2 = line.strip().split(" ")
    print(words2)

def main():
   word2idx(mdstpl.cache_stats_words)

if __name__ == '__main__':
   main()


