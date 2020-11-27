from __future__ import division
from __future__ import print_function
import datetime
import templates.mon.tpl as montpl
import common.utils as utils

from bokeh.plotting import figure, output_file, show
from bokeh.models import CustomJS, Dropdown, ColumnDataSource, Select, Button
from bokeh.layouts import column, row, widgetbox
import pandas as pd
from bokeh.models import HoverTool
import itertools
from bokeh.palettes import Dark2_5 as palette

osd_fail_reports = []
osd_fails_per_hour = {}

start_ts = datetime.datetime.now()

mon_flaps = []
mon_flaps_per_hour = {}

slow_requests = []
slow_requests_per_hour = {}

def is_mon_flap(words, wdlen):
    return utils.log_compare(words, montpl.mon_flap_words, montpl.mon_flap_index_list)

def process_mon_flap(words):
    mon_flap = {}
    mon_flap["time"] = words[0] + "-" + words[1]
    for key in montpl.mon_flap_key2idx.keys():
       idx = montpl.mon_flap_key2idx[key]
       mon_flap[key] = words[idx]
    mon_flaps.append(mon_flap)

def check_mon_flaps(words, wdlen):
    if is_mon_flap(words, wdlen):
       process_mon_flap(words)
       return True
    else:
       return False

def is_osd_fail_report(words, wdlen):
    return utils.log_compare(words, montpl.osd_fail_words, montpl.osd_fail_index_list)

def process_osd_fail_report(words):
    osd_fail = {}
    osd_fail["time"] = words[0] + "-" + words[1]
    for key in montpl.osd_fail_key2idx.keys():
       idx = montpl.osd_fail_key2idx[key]
       osd_fail[key] = words[idx]
    osd_fail_reports.append(osd_fail)

def get_delta_hour(time):
   ts = utils.timestamp(time);
   delta_hour = (ts - start_ts).total_seconds() / 3600
   return int(delta_hour)

def gen_count_per_hour(reports, res):
    for report in reports:
       dh = get_delta_hour(report["time"])
       if res.has_key(dh):
          res[dh] += 1
       else:
          res[dh] = 1


def get_start_timestamp(fp):
   first_line = fp.readline()
   words = utils.log_split(first_line)
   return utils.timestamp(words[0] + "-" + words[1])

def check_osd_fail_report(words, wdlen):
    if is_osd_fail_report(words, wdlen):
       process_osd_fail_report(words)
       return True
    else:
       return False

def is_slow_requests(line):
    return utils.log_match(line, montpl.slow_requests_match_list)

def process_slow_requests(words, wdlen):
    slow_request = {}
    slow_request["time"] = words[0] + "-" + words[1]
    slow_requests.append(slow_request)

def check_slow_requests(line, words, wdlen):
    if is_slow_requests(line):
       process_slow_requests(words, wdlen)
       return True
    else:
       return False

def gen_mon_stats():
    gen_count_per_hour(osd_fail_reports, osd_fails_per_hour)
    gen_count_per_hour(mon_flaps, mon_flaps_per_hour)
    gen_count_per_hour(slow_requests, slow_requests_per_hour)


def print_monstat_bokeh():
    total_stats = {
                   "osd_fails": osd_fails_per_hour,
                   "mon_flaps": mon_flaps_per_hour,
                   "slow_requests": slow_requests_per_hour
                  }
    output_file("output/mon_stats.html")
    p = figure(plot_width=800, plot_height=600, x_axis_label='time(hour)', y_axis_label='number')

    colors = itertools.cycle(palette)
    for key, color in zip(total_stats.keys(), colors):
       x, y = utils.gen_kv_list(total_stats[key])
       p.circle(x = x, y = y, legend_label=key, size=8, color=color)
    show(p)

def print_monstat_text():
    print("monstat text printing")
    print(osd_fails_per_hour)
    print(mon_flaps_per_hour)

def print_monstat(mode):
    gen_mon_stats()
    if mode == "bokeh":
       print_monstat_bokeh()
    else:
       print_monstat_text()


def start_parse_mon_log(filepath, mode):
   with open(filepath) as fp:
       #import pdb
       #pdb.set_trace()
       global start_ts
       start_ts = get_start_timestamp(fp)
       for line in fp:
          words = utils.log_split(line)
          wdlen = len(words)
          if utils.check_err_log(words, line):
             continue
          if (check_osd_fail_report(words, wdlen)):
             continue
          if (check_mon_flaps(words, wdlen)):
             continue
          if check_slow_requests(line,words, wdlen):
             continue
       print_monstat(mode)
       utils.dump_errors()


