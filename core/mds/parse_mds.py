#2020-08-31 07:09:19.141 7fe4a4b8f700  2 mds.0.cache Memory usage:  total 15075176, rss 14665904, heap 330416, baseline 330416, 3181526 / 3662455 inodes have caps, 3183808 caps, 0.86931 caps per inode

from __future__ import division
from bokeh.plotting import figure, output_file, show
from bokeh.models import CustomJS, Dropdown, ColumnDataSource, Select, Button
from bokeh.layouts import column, row, widgetbox
import pandas as pd
from bokeh.models import HoverTool

import templates.mds.tpl as mdstpl
import common.utils as utils

mds_cache_stats = []

def is_cache_stats(words, wdlen):
   return utils.log_compare(words, mdstpl.cache_stats_words, mdstpl.cache_stats_index_list)

def fill_mds_cache_stats(words):
   cache_stat = {}
   cache_stat["time"] = words[0] + "-" + words[1]
   for key in mdstpl.cache_stats_key2idx.keys():
      idx = mdstpl.cache_stats_key2idx[key]
      cache_stat[key] = words[idx]
   mds_cache_stats.append(cache_stat)

def check_cache_stats(words, wdlen):
  if is_cache_stats(words, wdlen):
     fill_mds_cache_stats(words)
     return True
  else:
     return False

def gen_element_in_diclist(mds_cache_stats, key):
  return [mcs[key] for mcs in mds_cache_stats]

def print_mcs_bokeh():
   
   TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset,hover,save"

   
   time = utils.gen_element_in_diclist(mds_cache_stats, "time")
   timestamp = [utils.timestamp(x) for x in time]
   xtime = [(x - timestamp[0]).total_seconds() for x in timestamp]
   #print xtime
   xinodes = utils.gen_element_in_diclist(mds_cache_stats, "inodes")
   inodes = [int(x) for x in xinodes]
   #inodes[0] = 10000
   xcaps = utils.gen_element_in_diclist(mds_cache_stats, "caps")
   caps = [int(x) for x in xcaps]
   print caps
   
   TOOLTIPS=[ ("(x, y)", "x:$x y:$y"), ("time", "time:@time"), ("caps", "caps:@caps"), ("inodes", "inodes:@inodes")]
   all_data = {"xtime": xtime, "time" : time, "inodes": inodes, "caps" : caps}
   hover = HoverTool(
    tooltips = TOOLTIPS
   )
   pd.options.display.max_rows = 300000000
   df = pd.DataFrame(all_data)
    
   source = ColumnDataSource(df)
   #source = ColumnDataSource(data = dict(x = xtime, y = inodes))

   output_file("inodes.html")
   #p = figure(plot_width=800, plot_height=600, x_axis_label='timestamp', y_axis_label='inode number')
   p = figure(plot_width=800, plot_height=600, tools = TOOLS, active_scroll = 'wheel_zoom', tooltips=TOOLTIPS, x_axis_label='timestamp', y_axis_label='inode number')
   p.add_tools(hover)
   p.circle('xtime', 'inodes', source = source, legend_label="inodes", size=3, color="red")
   p.circle(x = "xtime", y = "caps", source = source, legend_label="caps", size=3, color="black")
   #p.line('x', 'y', source = source, legend_label=inodes, line_color="blue", line_dash="4 4")
   show(p)   
   print "bokeh output"

def print_mcs_text():
   print "text output"

def print_mcs(mode):
   if mode == "bokeh":
      print_mcs_bokeh()
   elif mode == "text":
      print_mcs_text()
   elif mode == "all":
      print_mcs_text()
      print_mcs_bokeh()
   

def start_parse_mds_log(filepath, mode):
   with open(filepath) as fp:
       for line in fp:
          words = utils.log_split(line)
          wdlen = len(words)
          if utils.check_err_log(words, line):
             continue
          if (check_cache_stats(words, wdlen)):
             continue
   print_mcs(mode)

