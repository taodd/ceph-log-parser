#!/usr/bin/python

from __future__ import print_function
import sys
import os
import argparse
import core.mds.parse_mds as parse_mds
import core.mon.parse_mon as parse_mon
import core.osd.parse_osd as parse_osd
import common.utils as utils

# main.py -f <file> [-d <directory>] -m <bokeh/text>

def parse_args():
   parser = argparse.ArgumentParser()
   parser.add_argument("-m", "--mode", default="text", help='choose the output mode as bokeh or text')
   parser.add_argument("-d", "--directory", help='target directory to be parsed')
   parser.add_argument("-f", "--file", help='target log file to be parsed')
   parser.add_argument("-t", "--type", help='target daemon type log file')
   args = parser.parse_args()
   return vars(args)

def main():
  args = parse_args()
  filepath = args['file']
  mode = args['mode']
  tp = args['type']
  print(args)
  if not os.path.isfile(filepath):
       print("File path {} does not exist. Exiting...".format(filepath))
       sys.exit()
  if (tp == "mon"):
     parse_mon.start_parse_mon_log(filepath, mode)
  if (tp == "mds"):
     parse_mds.start_parse_mds_log(filepath, mode)
  if (tp == "osd"):
     parse_osd.start_parse_osd_log(filepath, mode)
  utils.dump_errors()

if __name__ == '__main__':
   main()

