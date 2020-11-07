#!/usr/bin/python

from __future__ import division
from bokeh.plotting import figure, output_file, show
from bokeh.models import CustomJS, Dropdown, ColumnDataSource, Select, Button
from bokeh.layouts import column, row, widgetbox


import json
import os
import sys


def get_osdid(filename):
   wds = filename.split("-")
   return wds[-4]

def get_osdnum(osdid):
   wds = osdid.split(".")
   return wds[1]

def get_time(filename):
   wds = filename.split("-")
   lwds = wds[-1].split(".")
   return lwds[0]

def get_penalty_write_ratio(jp):
   penalty_writes = jp["bluestore"]["write_penalty_read_ops"]
   small_writes = jp["bluestore"]["bluestore_write_small"]
   #print  penalty_writes, small_writes
   if small_writes == 0:
      return -1
   else:
      return penalty_writes / small_writes

def get_total_ops(jp):
   ops = jp["osd"]["op"]
   subops = jp["osd"]["subop"]
   return ops + subops

def get_rid_of_outosds(osds):
   for osd in osds.keys():
      if osds[osd]["1"]["total_ops"] == 0:
         del osds[osd]

def avg(lst):
   return sum(lst) / len(lst)

def mid(lst):
   lst.sort(key = lambda item: int(item))
   return lst[int(len(lst)/2)]

def get_osdlist(osds):
   keys = osds.keys()
   return [ osd for osd in sorted(keys, key = lambda item: int(get_osdnum(item)))]


def geny_tops(osds, osdid):
   osd_dic = osds[osdid]
   ytops = []
   for time in sorted(osd_dic.keys(), key = lambda item: int(item)):
      ytops.append(osd_dic[time]["total_ops"])
   ytops.pop(0)
   return ytops

def genx_time(osds):
   xtime = [int(x) for x in sorted(osds[next(iter(osds))].keys(), key = lambda item: int(item))]
   xtime.pop(0)
   return xtime

def get_mid_ops(osds):
   osd_keys = osds.keys()
   osd_times = sorted(osds[next(iter(osds))].keys(), key = lambda item: int(item))
   res = []
   for time in osd_times:
      mval = mid([osds[osd][time]["total_ops"] for osd in osd_keys])
      res.append(mval)
   res.pop(0)
   return res

directory = sys.argv[1]
osds = {}
for filename in os.listdir(directory):
   if filename.find("perf-dump") >= 0:
      filepath = os.path.join(directory, filename)
      if os.path.getsize(filepath) == 0:
          continue
      f = open(filepath)
      ##print "start decode", filename
      jp = json.load(f)
      osdid = get_osdid(filename)
      time = get_time(filename)
      #print "osd ", osdid
      if osdid not in osds:
         osds[osdid] = {}
      if time not in osds[osdid]:
         osds[osdid][time] = {}
      osds[osdid][time]["op_r_process_latency"] = jp["osd"]["op_r_process_latency"]["avgtime"]
      osds[osdid][time]["subop_w_latency"] = jp["osd"]["subop_w_latency"]["avgtime"]
      osds[osdid][time]["read_lat"] = jp["bluestore"]["read_lat"]["avgtime"]
      osds[osdid][time]["commit_lat"] = jp["bluestore"]["commit_lat"]["avgtime"]
     #penalty write
      osds[osdid][time]["write_penalty_ratio"] = get_penalty_write_ratio(jp)
      osds[osdid][time]["total_ops"] = get_total_ops(jp)

get_rid_of_outosds(osds)


for osd in sorted(osds.keys(), key = lambda item: int(get_osdnum(item))):
  osd_dic = osds[osd]
  tops = []
  for time in sorted(osd_dic.keys(), key = lambda item: int(item)):
     tops.append(osd_dic[time]["total_ops"])
  tops.pop(0)


x0 = genx_time(osds)
y0 = geny_tops(osds, "osd.0")
source = ColumnDataSource(data = dict(x = x0, y = y0)) 

output_file("cc1.html")
p = figure(plot_width=600, plot_height=400, x_axis_label='time period', y_axis_label='total ops')
p.circle('x', 'y', source = source, legend_label=osd, size=5, fill_color="red")
p.line('x', 'y', source = source, legend_label=osd, line_color="blue", line_dash="4 4")

callback = CustomJS(args=dict(source=source, osds=osds), code="""
    var data = source.data;
    var f = cb_obj.value
    var y = data['y']
    var x = data['x']
    for (var i = 0; i < x.length; i++) {
        y[i] = osds[f][x[i]]["total_ops"]
    }
    source.change.emit();
""")

menu = get_osdlist(osds)
select = Select(title = "choose osd", value = "osd.0", options = menu)
select.js_on_change("value", callback)

mid_ops = get_mid_ops(osds)
# To do, use javascript to calculate the mid value instead of python
callback_button = CustomJS(args=dict(source=source, mid_ops=mid_ops), code="""
    var data = source.data;
    var y = data['y']
    var x = data['x']
    for (var i = 0; i < x.length; i++) {
        y[i] = mid_ops[i]
    }
    source.change.emit();

""")

button = Button(label="mid", button_type="success")
button.js_on_click(callback_button)

layout = row(widgetbox(select, button), p)
show(layout)
# add a circle renderer with a size, color, and alpha
