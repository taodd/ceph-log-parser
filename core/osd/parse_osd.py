from __future__ import division
import sys
import os
import time
import datetime
import re

import common.utils as utils
import templates.osd.tpl as osdtpl

import pandas as pd

from bokeh.plotting import figure, output_file, show
from bokeh.models import CustomJS, Dropdown, ColumnDataSource, CheckboxGroup, Select, Button, Slider
from bokeh.layouts import column, row, widgetbox
from bokeh.models import HoverTool

def is_bs_write_begin(words):
    return utils.log_compare(words, osdtpl.bs_write_begin_words, osdtpl.bs_write_bi_list)

def is_bs_write_end(words):
    return utils.log_compare(words, osdtpl.bs_write_end_words, osdtpl.bs_write_ei_list)

def process_bs_write_begin(words, begin):
    bs_wb = {}
    time = words[0] + "-" + words[1]
    bs_wb["time"] = time
    for key in osdtpl.bs_write_begin_key2idx.keys():
       idx = osdtpl.bs_write_begin_key2idx[key]
       bs_wb[key] = words[idx]
    begin[bs_wb["thread"]] = bs_wb

def process_bs_write_end(words, begin, stats):
    bs_we = {}
    time = words[0] + "-" + words[1]
    bs_we["time"] = time
    stat = {}
    for key in osdtpl.bs_write_end_key2idx.keys():
        idx = osdtpl.bs_write_end_key2idx[key]
        bs_we[key] = words[idx]
    if begin.has_key(bs_we["thread"]):
       bs_wb = begin[bs_we["thread"]]
       stat["start_time"] = bs_wb["time"]
       # Use microseconds for latency
       stat["latency"] = int(utils.time_substract(bs_we["time"], bs_wb["time"]) * 1000000)
       stat["aligned"] = utils.is_aligned(bs_we["offlen"], 4096)
       stat["len"] = utils.get_len(bs_we["offlen"])
       stat["offset"] = utils.get_offset(bs_we["offlen"])
       stat["type"] = "bs_write"
       stats.append(stat)
       del begin[bs_we["thread"]]

def print_bluestore_latency(bs_stats, mode):
    if mode == "bokeh":
       print_bluestore_latency_bokeh(bs_stats)
    elif mode == "text":
       for stat in bs_stats:
          print stat

def get_color(type):
    if type == "bs_write":
       return "red"
    elif type == "bs_read":
       return "green"

def gen_bs_data_frame(bs_stats):
    bs_stime = utils.gen_element_in_diclist(bs_stats, "start_time")
    bs_lat = utils.gen_element_in_diclist(bs_stats, "latency")
    bs_len = utils.gen_element_in_diclist(bs_stats, "len")
    bs_align = utils.gen_element_in_diclist(bs_stats, "aligned")
    bs_ts = [utils.timestamp(x) for x in bs_stime]
    bs_color = ["green" for x in bs_stime] 
    all_data = { "ts": bs_ts, "align": bs_align, 
                "length": bs_len, "lat": bs_lat, "color": bs_color}
    df = pd.DataFrame(all_data)
    return df
         
def get_df_subset(df, colume, value):
    subdf = df[df[colume] == value]
    return subdf

def print_bs_latency(plot_name, bs_stats):
    df = gen_bs_data_frame(bs_stats)
    
    output_file(plot_name)
    
    TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset,hover,save"

    TOOLTIPS=[("ts", "ts:@ts"), ("lat", "lat:@lat"), ("length", "length:@length"), ("align", "align:@align")]
    
    hover = HoverTool(
    tooltips = TOOLTIPS
    )
    p = figure(plot_width=800, plot_height=600, tools = TOOLS, tooltips = TOOLTIPS, active_scroll = 'wheel_zoom', x_axis_label='time', y_axis_label='latency') 
    p.add_tools(hover)
    
    orig_source = ColumnDataSource(df) 
    source = ColumnDataSource(data = dict(ts=[], lat=[], length=[], align=[], color=[])) 
    p.circle('ts','lat', source = source, legend_label=plot_name, size=5, fill_color='color')
    slider_length = Slider(start=0, end=4194304, value=0, step=1, title="length")
    slider_sample = Slider(start=0, end=1, value=0, step=.1, title="sample")
    button_align = Button(label="Not Aligned", button_type="success")
    
    callback_button = CustomJS(args=dict(source=source), code="""
                               var data = source.data
                               var align = data['align'] 
                               var color = data['color']
                               for(var i = 0; i < color.length; ++i) {
                                    if(!align[i]) {
                                       color[i] = "red" 
                                    }
                                }
                                source.change.emit()
                               """)
    button_align.js_on_click(callback_button)

    callback = CustomJS(args=dict(orig_source=orig_source, source=source, 
                                 slider_length=slider_length, slider_sample=slider_sample),
                                 code="""
       
        function getRandomSubset(myArray,nb_picks)
        {
           for (i = myArray.length-1; i > 1  ; i--)
           {
              var r = Math.floor(Math.random()*i);
              var t = myArray[i];
              myArray[i] = myArray[r];
              myArray[r] = t;
           }

           return myArray.slice(0,nb_picks);
        }
        
        var orig_data = orig_source.data
        var data = source.data
        const len_v = slider_length.value
        const sample_v = slider_sample.value        
        
        console.log(orig_data)
        console.log(data)
        var ts = data['ts']
        var lat = data['lat']
        var len = data['length']
        var align = data['align']
        var color = data['color']
        ts.length = 0
        lat.length = 0
        len.length = 0
        align.length = 0
        color.length = 0
        var olen = orig_data['length']
        var idx_arr = []
        for (var i = 0; i < olen.length; i++) {
           idx_arr.push(i) 
        }
        console.log(idx_arr)
        console.log(sample_v)
        var samples = getRandomSubset(idx_arr, Math.floor(sample_v * idx_arr.length));
        samples.sort(function(a, b){return a-b})
        console.log(samples)
        console.log("after getRandomSubset")
        for (var i = 0; i < samples.length; i++) {
           var idx = samples[i]
           if (orig_data['length'][idx] < len_v) {
              ts.push(orig_data['ts'][idx])
              lat.push(orig_data['lat'][idx])
              len.push(orig_data['length'][idx])
              align.push(orig_data['align'][idx]) 
              color.push(orig_data['color'][idx]) 
           }
        }

        source.change.emit();
    """)

    slider_sample.js_on_change('value', callback)
    slider_length.js_on_change('value', callback)
    p.legend.click_policy="hide"
    layout = row(column(slider_sample, slider_length, button_align), p)
    show(layout)
 
def print_bluestore_latency_bokeh(bs_stats):
    # one length scaler to filter the op that doesn't fit the length
    # sample number controller bar
    # latency checkbox (probably will need multiple sources)
    # align button
    df = gen_bs_data_frame(bs_stats)
    output_file("osd_lat.html")
    p = figure(plot_width=600, plot_height=400, x_axis_label='time', y_axis_label='latency') 
    orig_source_bsw = ColumnDataSource(df)
    
    '''
    ### Checkbox ###    
    callback_checkbox = CustomJS( args=dict(source_bsw = source_bws), code="""
         
    """)
    LABELS = ["bluestore write", "bluestore read"]
    checkbox_group = CheckboxGroup(labels=LABELS, active=[])
    checkbox_group.js_on_change('active', callback_checkbox)
    '''
    #print orig_source_bsw.data
    '''
    all_data = { "bsw_ts": bsw_ts, "bsw_type": bsw_type, "bsw_align": bsw_align, 
                "bsw_len": bsw_len, "bsw_lat": bsw_lat, "bsw_color": bsw_color }
    '''
    cur_source_bsw = ColumnDataSource(data = dict(bsw_ts=[], bsw_lat=[], bsw_len=[], 
                                                  bsw_type=[], bsw_color=[], bsw_align=[]))
    ### be careful, never use source assignment
    #cur_source_bsw = orig_source_bsw 
    
    p.circle('bsw_ts','bsw_lat', source = cur_source_bsw, legend_label='bsw_type', size=5, fill_color='bsw_color')
    #p.multi_line('bsw_ts','bsw_lat', source = orig_source_bsw, legend_label='bsw_type', line_color='bsw_color', line_dash="5 4")
    
    slider_length = Slider(start=0, end=4194304, value=1048576, step=1, title="length")
    slider_sample = Slider(start=0, end=1, value=0, step=.1, title="sample")
    callback = CustomJS(args=dict(orig_source=orig_source_bsw, source=cur_source_bsw, slider_length=slider_length, slider_sample=slider_sample), code="""
        console.log("before getRandomSubset")
        function getRandomSubset(myArray,nb_picks)
        {
           for (var i = myArray.length-1; i > 1  ; i--)
           {
              var r = Math.floor(Math.random()*i);
              var t = myArray[i];
              myArray[i] = myArray[r];
              myArray[r] = t;
           }

           return myArray.slice(0,nb_picks);
        }
        var orig_data = orig_source.data
        var data = source.data
        const len = slider_length.value
        const sample = slider_sample.value        

        console.log(orig_data)
        console.log(data)
        var x = data['bsw_ts']
        var y = data['bsw_lat']
        var l_col = data['bsw_len']
        var a_col = data['bsw_align']
        x.length = 0
        y.length = 0
        l_col.length = 0
        a_col.length = 0
        var l = orig_data['bsw_len']
        var idx_arr = []
        for (var i = 0; i < l.length; i++) {
           idx_arr.push(i) 
        }
        console.log(idx_arr)
        console.log(sample)
        var samples = getRandomSubset(idx_arr, Math.floor(sample * idx_arr.length));
        samples.sort(function(a, b){return a-b})
        console.log(samples)
        console.log("after getRandomSubset")
        for (var i = 0; i < samples.length; i++) {
           var idx = samples[i]
           if (orig_data['bsw_len'][idx] < len) {
              x.push(orig_data['bsw_ts'][idx])
              y.push(orig_data['bsw_lat'][idx])
              l_col.push(orig_data['bsw_len'][idx])
              a_col.push(orig_data['bsw_align'][idx]) 
           }
        }

        source.change.emit();
        console.log("callback completed");
    """)
    ## we choose slider "sample" having higher priority than "length"
    
    slider_sample.js_on_change('value', callback)
    slider_length.js_on_change('value', callback)
    p.legend.click_policy="hide"
    layout = row(column(slider_sample, slider_length), p)
    show(layout)

def is_bs_read_begin(words):
    return utils.log_compare(words, osdtpl.bs_read_begin_words, osdtpl.bs_read_bi_list)

def is_bs_read_end(words):
    return utils.log_compare(words, osdtpl.bs_read_end_words, osdtpl.bs_read_ei_list)

def process_bs_read_begin(words, begin):
    bs_rb = {}
    time = words[0] + "-" + words[1]
    bs_rb["time"] = time
    for key in osdtpl.bs_read_begin_key2idx.keys():
       idx = osdtpl.bs_read_begin_key2idx[key]
       bs_rb[key] = words[idx]
    begin[bs_rb["thread"]] = bs_rb

def process_bs_read_end(words, begin, stats):
    bs_re = {}
    time = words[0] + "-" + words[1]
    bs_re["time"] = time
    stat = {}
    for key in osdtpl.bs_read_end_key2idx.keys():
       idx = osdtpl.bs_read_end_key2idx[key]
       bs_re[key] = words[idx]
    if begin.has_key(bs_re["thread"]):
       bs_rb = begin[bs_re["thread"]]
       stat["start_time"] = bs_rb["time"]
       stat["latency"] = utils.time_substract(bs_re["time"], bs_rb["time"]) * 1000000
       stat["aligned"] = utils.is_aligned(bs_re["offlen"], 4096)
       stat["len"] = utils.get_len(bs_re["offlen"])
       stat["offset"] = utils.get_offset(bs_re["offlen"])
       stat["type"] = "bs_read"
       stats.append(stat)
    
       del begin[bs_re["thread"]]

def is_bs_penalty_read_begin(words):
    return False

def is_bs_penalty_read_end(words):
    return False

## currently use enqueue_op as the start point of osd op

##not repop
def is_op(word):
    return re.search(osdtpl.op_key, word) != None
'''
def is_read_op_start(line, words):
    if utils.log_compare_without_len(words, osdtpl.read_op_words, osdtpl.read_op_idx_list):
       if utils.log_match(line, osdtpl.read_op_match_list):
          if get_osd_op_type(line) == "unknown":
             print "Got an unknown type",  line
         # print "read op start", line
          return True
    return False
'''

def is_read_op_start(line, words):
    if is_enqueue_op(words):
        if is_op(words[osdtpl.enqueue_op_key2idx["opid"]]) and get_osd_op_type(line) == "read":
           return True
    return False 

def process_read_op_start(line, words, rops):
    op = process_enqueue_op(line, words, rops)
    rops[op["opid"]] = op 

def is_ms_op_reply(line, words):
## could be read or write, need to identify in process_foo
    if utils.log_compare_without_len(words, osdtpl.ms_op_reply_words, osdtpl.ms_op_reply_idx_list):
       if utils.log_match(line, osdtpl.ms_op_reply_match_list):
          return True
    return False

def get_op_reply_tid(reply_id):
    wds = reply_id.split("(")
    return wds[-1] 
def get_op_tid(opid):
    wds = opid.split(":")
    return wds[-1]

'''
def check_and_process_read_op_reply(line, words, rops):
    op_reply = {}
    if is_ms_op_reply(line, words):
       for key in osdtpl.ms_op_reply_key2idx.keys():
           idx = osdtpl.ms_op_reply_key2idx[key]
           op_reply[key] = words[idx]
       op_reply["reply_time"] = words[0] + "-" + words[1]
       dst = op_reply["dst"]
       tid = get_op_reply_tid(op_reply["reply_id"])
       for opid in rops.keys():
           op = rops[opid]
           if dst == op["src"] and tid == get_op_tid(op["opid"]): #same client and tid
              op["latency"] = utils.time_substract(op_reply["reply_time"], op["dispatch_time"])
              #print "read op reply", line
              return True
    return False
'''

def gen_read_op_df(rops):
    #import pdb; pdb.set_trace();
    ops_diclist = utils.gen_v_list(rops)
    enqueue_time = utils.gen_element_in_diclist(ops_diclist, "enqueue_time")
    opts = [utils.timestamp(x) for x in enqueue_time]
    opid = utils.gen_element_in_diclist(ops_diclist, "opid")
    before_enqueue_lat = utils.gen_element_in_diclist(ops_diclist, "before_enqueue_lat")
    reply_time = utils.gen_element_in_diclist(ops_diclist, "reply_time")
    eop_lat = [utils.time_substract(reply_time[idx], enqueue_time[idx]) for idx in range(len(enqueue_time))]
    op_lat = [float(eop_lat[idx]) + float(before_enqueue_lat[idx]) for idx in range(len(eop_lat))]
    print op_lat
    queue_lat = utils.gen_element_in_diclist(ops_diclist, "queue_latency")
    dequeue_lat = utils.gen_element_in_diclist(ops_diclist, "dequeue_latency")
    dequeue_count = utils.gen_element_in_diclist(ops_diclist, "dequeue_count")
    
    all_data = {"opid": opid, 
                "opts": opts, 
                "op_lat": op_lat, 
                "enqueue_time": enqueue_time,
		"before_enqueue_lat": before_enqueue_lat, 
                "queue_lat": queue_lat,
                "dequeue_lat": dequeue_lat, 
                "dequeue_count": dequeue_count
               }
  
    return pd.DataFrame(all_data) 

def print_read_op_latency(rops):
    df = gen_read_op_df(rops) 
    output_file("osd_read_op")
    
    TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset,hover,save"
    TOOLTIPS=[
              ("opid", "opid"), 
              ("enqueue_time", "@enqueue_time"), 
              ("op_lat","@op_lat"),
              ("before_enqueue_lat", "@before_enqueue_lat"), 
              ("queue_lat","@queue_lat"),
              ("dequeue_lat", "@dequeue_lat"),
              ("dequeue_count", "@dequeue_count")
             ]
    hover = HoverTool(
            tooltips = TOOLTIPS
            )

    p = figure(plot_width=800, plot_height=600, tools = TOOLS, tooltips = TOOLTIPS, active_scroll = 'wheel_zoom', x_axis_label='time', y_axis_label='latency') 
    p.add_tools(hover)
    
    source = ColumnDataSource(df)
    p.circle('opts', 'op_lat', source = source, legend_label="osd read op", size=5, fill_color="green")
    show(p)

def is_write_op_start(line, words):
    if is_enqueue_op(words):
        if is_op(words[osdtpl.enqueue_op_key2idx["opid"]]) and get_osd_op_type(line) == "write":
           return True
    return False

def process_write_op_start(line, words, wops):
    op = process_enqueue_op(line, words, wops)
    wops[op["opid"]] = op

def is_write_op_end(line):
    return utils.log_match(line, osdtpl.op_reply_match_list)

def process_write_op_end(words, ops):
    #op round trip time = time(send reply to client) - time(enqueue_op)
    opkey = ""
    for w in words:
       if utils.re_match(w, osdtpl.op_reply_key):
          opkey = w
          break
    time = words[0] + "-" + words[1]
    if ops.has_key(opkey):
      ops[opkey]["reply_time"] = time 

def is_subop_sent(line, words):
    if utils.log_compare_without_len(words, osdtpl.subop_words, osdtpl.subop_idx_list):
       if utils.log_match(line, osdtpl.subop_match_list):
          return True
    return False

def process_subop_sent(words, wops):
   subop = {}
   for k in osdtpl.subop_key2idx.keys():
      v = osdtpl.subop_key2idx[k]
      subop[k] = words[v]
   subop["time"] = words[0] + "-" + words[1]
   subop["subosd"] = "unknown"
   subop["latency"] = "unknown"
   opid = repop2op(subop["subop_id"])
   
   if wops.has_key(opid):
      if not wops[opid].has_key("subop"):
         wops[opid]["subop"] = []
      wops[opid]["subop"].append(subop)
   else:
      pass 

def repop2op(repop):
    #osd_repop(client.4129.0:8373 -> osd_op(client.4129.0:8373
    wds = repop.split("(")
    op = "osd_op" + "(" + wds[1]
    return op

def repop_reply2op(repop_reply):
    #osd_repop_reply(client.4129.0:8373 -> osd_op(client.4129.0:8373
    wds = repop_reply.split("(")
    op = "osd_op" + "(" + wds[1]
    return op

def is_subop_reply(line, words):
    if utils.log_compare_without_len(words, osdtpl.subop_reply_words, osdtpl.subop_reply_idx_list):
       if utils.log_match(line, osdtpl.subop_reply_match_list):
          return True
    return False

def process_subop_reply(words, wops):
    subop_reply = {}
    subop_reply["time"] = words[0] + "-" + words[1] 
    
    for k in osdtpl.subop_reply_key2idx.keys():
        v = osdtpl.subop_reply_key2idx[k]
        subop_reply[k] = words[v]
    opid = repop_reply2op(subop_reply["subop_reply_id"])
    if wops.has_key(opid):
       # Since this is a subop reply, subop sent must already been processed
       assert wops[opid].has_key("subop")
       for subop in wops[opid]["subop"]:
           if subop["dst"] == subop_reply["src"]:
              subop["latency"] = utils.time_substract(subop_reply["time"], subop["time"])
              subop["subosd"] =  subop_reply["subosd"]

def is_repop_start(words):
    return False

def is_repop_end(words):
    return False

def is_enqueue_op(words):
    return utils.log_compare_without_len(words, osdtpl.enqueue_op_words, osdtpl.enqueue_op_idx_list)

def is_dequeue_op_start(words):
    return utils.log_compare_without_len(words, osdtpl.dequeue_op_start_words, osdtpl.dequeue_op_start_idx_list) 

def process_dequeue_op_start(words, wops, rops):
    dequeue = {}
    dequeue["time"] = words[0] + "-" + words[1]
    for key in osdtpl.dequeue_op_start_key2idx.keys():
        idx = osdtpl.dequeue_op_start_key2idx[key]
        dequeue[key] = words[idx]
    for ops in [wops, rops]:
        if ops.has_key(dequeue["opid"]):
           op = ops[dequeue["opid"]]
           op["dequeue_time"] = dequeue["time"]
           op["queue_latency"] = str(utils.time_substract(dequeue["time"], op["enqueue_time"]))
           if op.has_key("dequeue_count"):
              op["dequeue_count"] += 1
           else:
              op["dequeue_count"] = 1 
           op["dequeue_thread"] = dequeue["thread"]

def is_dequeue_op_end(words):
    return utils.log_compare(words, osdtpl.dequeue_op_end_words, osdtpl.dequeue_op_end_idx_list)

def process_dequeue_op_end(words, wops, rops):
    dequeue_end = {}
    dequeue_end["time"] = words[0] + "-" + words[1]
    for key in osdtpl.dequeue_op_end_key2idx.keys():
        idx = osdtpl.dequeue_op_end_key2idx[key]
        dequeue_end[key] = words[idx]
    for ops in [wops, rops]:
        for op in ops.values():
            if op.has_key("dequeue_thread"): ## means it is still in the osd dequeue thread
               if op["dequeue_thread"] == dequeue_end["thread"]:
                  op["dequeue_latency"] = str(utils.time_substract(dequeue_end["time"], op["dequeue_time"]))
                  if op["op_type"] == "read":
		       ## for read, it is also the end of a read op
                       op["reply_time"] = dequeue_end["time"]
                  del op["dequeue_thread"]

# This is now the start of an osd op, we might change it later when we start develop the messenger level
def process_enqueue_op(line, words, ops):
    #time spent on messenger level: time(enqueue_op) - time(messenger receive the first byte)
    op = {}
    time = words[0] + "-" + words[1]
    op["enqueue_time"] = time
    op["op_type"] = get_osd_op_type(line)
    for key in osdtpl.enqueue_op_key2idx.keys():
       idx = osdtpl.enqueue_op_key2idx[key]
       op[key] = words[idx]
    return op
   

def get_osd_op_type(line):
    if re.search("\\+write\\+", line) != None:
       return "write"
    elif re.search("\\+read\\+", line) != None:
       return "read"
    else:
       return "unknown"

def get_osd_op_color(op_type):
    type2color = {"write":"red", "read":"green", "unknown":"black"}
    return type2color[op_type]

def gen_subop_str(sos):
    sstr = ""
    #print sos
    for so in  sos:
       sstr += "["
       sstr += so["subosd"] + " : " + str(so["latency"])
       sstr += "] "
    return sstr

def gen_write_op_df(ops):
    ops_diclist = utils.gen_v_list(ops)
    enqueue_time = utils.gen_element_in_diclist(ops_diclist, "enqueue_time")
    opts = [utils.timestamp(x) for x in enqueue_time]
    reply_time = utils.gen_element_in_diclist(ops_diclist, "reply_time")
    opid = utils.gen_element_in_diclist(ops_diclist, "opid")
    opref = utils.gen_element_in_diclist(ops_diclist, "opref")
    before_enqueue_lat = utils.gen_element_in_diclist(ops_diclist, "before_enqueue_lat")
    ## currently just use reply_time - enqueue_time
    op_lat = [utils.time_substract(reply_time[idx], enqueue_time[idx]) for idx in range(len(enqueue_time))]
    ## construct subop
    for op in ops_diclist:
        if not op.has_key("subop"):
           pass
           #print "no subop", op
        else:
           pass
           #print "has subop", op
    subops = utils.gen_element_in_diclist(ops_diclist, "subop")
    subop_str = []
    for subs in subops:
       cstr = gen_subop_str(subs)
       subop_str.append(cstr)
       
    queue_lat = utils.gen_element_in_diclist(ops_diclist, "queue_latency")
    dequeue_lat = utils.gen_element_in_diclist(ops_diclist, "dequeue_latency")
    dequeue_count = utils.gen_element_in_diclist(ops_diclist, "dequeue_count")
    bluestore_lat = utils.gen_element_in_diclist(ops_diclist, "bluestore_lat")
    color = ["red" for x in bluestore_lat]
    all_data = {"opts": opts,
                "enqueue_time": enqueue_time, 
                "op_lat": op_lat, 
                "before_enqueue_lat": before_enqueue_lat, 
                "opid": opid, 
                "subop_str": subop_str,
                "queue_lat": queue_lat, 
                "dequeue_lat": dequeue_lat,
                "dequeue_count": dequeue_count,
                "bluestore_lat": bluestore_lat,
                "color": color
               } 
    df = pd.DataFrame(all_data)
    return df

def process_repop_start(words):
    pass

def process_repop_end(words):
    pass

def print_write_op_latency(ops):
    df = gen_write_op_df(ops)  
    output_file("osd_write_op")
    
    TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset,hover,save"
    
    # all_data = {"enqueue_time": enqueue_time, "op_lat": op_lat, "before_enqueue_lat": before_enqueue_lat, "opid": opid} 
    TOOLTIPS=[
              ("opid", "@opid"), 
              ("enqueue_time", "@enqueue_time"), 
              ("op_latency", "@op_lat"),  
              ("before_enqueue_lat", "@before_enqueue_lat"), 
              ("subops", "@subop_str"),
              ("queue_latency", "@queue_lat"),
              ("dequeue_latency", "@dequeue_lat"),
              ("dequeue_count", "@dequeue_count"),
              ("bluestore_latency", "@bluestore_lat")
             ]
    
    hover = HoverTool(
    tooltips = TOOLTIPS
    )
    
    p = figure(plot_width=800, plot_height=600, tools = TOOLS, tooltips = TOOLTIPS, active_scroll = 'wheel_zoom', x_axis_label='time', y_axis_label='latency') 
    p.add_tools(hover)
    
    source = ColumnDataSource(df)
    p.circle('opts', 'op_lat', source = source, legend_label="osd write op", size=5, color='color')
    
    slider = Slider(start=0, end=100, value=0, step=1, title="latency percentage")
    
    menu = ["before_enqueue_lat", "queue_lat", "dequeue_lat", "bluestore_lat"]
    select = Select(title = "choose latency type", value = "queue_time", options = menu)
    
    callback = CustomJS(args=dict(source=source, slider=slider, select=select), code="""
                        var throttle = slider.value
                        var ltype = select.value
                        console.log(throttle)
                        console.log(ltype)
                        var data = source.data
                        var color = data['color']
                        var bs_lat = data[ltype]
                        var op_lat = data['op_lat']
			console.log(bs_lat)
                        for(var i = 0; i < color.length; ++i) {
                           color[i] = "red"
                           percent = (bs_lat[i] / op_lat[i]) * 100
                           console.log(percent)
                           if (percent > throttle) {
                              color[i] = "green"
                           }
                        }
                        source.change.emit()
                        """
                        )
    slider.js_on_change('value', callback)     
    select.js_on_change("value", callback)
    layout = row(column(select,slider), p) 
    show(layout)

def remove_no_reply_op(ops):
    keys = ops.keys()
    for op in keys:
      if not ops[op].has_key("reply_time"):
         #print  "this op has no reply", ops[op]
         del ops[op]

def is_eval_repop(line, words):
    return utils.log_match(line, osdtpl.eval_repop_match_list)

def process_eval_repop(words, wops):
    #print "eval_repop", words
    eval_repop = {}
    eval_repop["time"] = words[0] + "-" + words[1]
    for key in osdtpl.eval_repop_key2idx.keys():
        idx = osdtpl.eval_repop_key2idx[key]
        eval_repop[key] = words[idx]
    for op in wops.values():
       if op.has_key("dequeue_thread"):
          if op["dequeue_thread"] == eval_repop["thread"]:
             op["eval_repop_time"] = eval_repop["time"]
             op["rep_tid"] = eval_repop["rep_tid"].split("=")[-1]
             break

def is_op_commit(line, words):
    return utils.log_compare_without_len(words, osdtpl.op_commit_words, osdtpl.op_commit_idx_list)

def process_op_commit(words, wops):
    #print "op_commit", words
    op_commit = {}
    op_commit["time"] = words[0] + "-" + words[1]
    for key in osdtpl.op_commit_key2idx.keys():
        idx = osdtpl.op_commit_key2idx[key]
        op_commit[key] = words[idx]
    for op in wops.values():
        if op.has_key("rep_tid"):
           if op["rep_tid"] == op_commit["rep_tid"]:
              op["bluestore_lat"] = utils.time_substract(op_commit["time"], op["eval_repop_time"])
              break

def start_parse_osd_log(filepath, mode):
    bsw_begin = {}
    bsw_stats = []
    bsr_begin = {}
    bsr_stats = []
    wops = {}
    rops = {}
    with open(filepath) as fp:
       for line in fp:
          words = utils.log_split(line)
          if is_bs_write_begin(words):
             process_bs_write_begin(words, bsw_begin)
             continue
          if is_bs_write_end(words):
             process_bs_write_end(words, bsw_begin, bsw_stats)
             continue
          if is_bs_read_begin(words):
             process_bs_read_begin(words, bsr_begin)
             continue
          if is_bs_read_end(words):
             process_bs_read_end(words, bsr_begin, bsr_stats)
             continue
          if is_bs_penalty_read_begin(words):
             continue
          if is_bs_penalty_read_end(words):
             continue
          if is_write_op_start(line, words):
             process_write_op_start(line, words, wops)
             continue
          if is_write_op_end(line):
             process_write_op_end(words, wops)
             continue
          if is_subop_sent(line, words):
             process_subop_sent(words, wops)
             continue
          if is_subop_reply(line, words):
             process_subop_reply(words, wops)
             continue
          if is_read_op_start(line, words):
             process_read_op_start(line, words, rops)
             continue
          '''
          if check_and_process_read_op_reply(line, words, rops):
             continue
           '''
          if is_repop_start(words):
             process_repop_start(words)
             continue
          if is_repop_end(words):
             process_repop_end(words)
             continue
          '''
          if is_enqueue_op(words):
             op = process_enqueue_op(line, words, ops)
             continue
          '''
          if is_dequeue_op_start(words):
             process_dequeue_op_start(words, wops, rops)
             continue
          if is_dequeue_op_end(words):
             process_dequeue_op_end(words, wops, rops)
             continue
          if is_eval_repop(line, words):
             process_eval_repop(words, wops)
             continue
          if is_op_commit(line, words):
             process_op_commit(words, wops)
             continue
             
          #if is_bs_read_begin()
       # remove those non completed ops
       remove_no_reply_op(wops)
       print_write_op_latency(wops)
       remove_no_reply_op(rops)
       print_read_op_latency(rops)
       #print_bs_latency("bluestore_alloc_write", bsw_stats)
       #print_bs_latency("bluestore_read", bsr_stats)
       

'''
def main():
  filepath = sys.argv[1]
  if not os.path.isfile(filepath):
       print("File path {} does not exist. Exiting...".format(filepath))
       sys.exit()
  wbegin = {}
  wlat = []
  rbegin = {}
  rlat = []
  prbegin = {}
  prlat = []
  dqbegin = {}
  dqlat = [] 
  with open(filepath) as fp:
       for line in fp:
          words = line.strip().split(' ')
          wdlen = len(words)
          if (wdlen == 9 and words[5] == "_write"):
              wbegin[words[2]] = words[0] + "-" + words[1]
          elif (wdlen == 11 and words[5] == "_write"):
              if wbegin.has_key(words[2]):
                    endtime = words[0] + "-" + words[1]
                    wlat.append((wbegin[words[2]], (timestamp(endtime) - timestamp(wbegin[words[2]])).total_seconds(), words[8], words[7]))
                    del wbegin[words[2]]
          elif (wdlen == 9 and words[5] == "read"):
              rbegin[words[2]] = words[0] + "-" + words[1]
          elif (wdlen == 11 and words[5] == "read"):
              if rbegin.has_key(words[2]):
                    endtime = words[0] + "-" + words[1]
                    rlat.append((rbegin[words[2]], (timestamp(endtime) - timestamp(rbegin[words[2]])).total_seconds(), words[8], words[7]))
                    del rbegin[words[2]]
          elif (wdlen == 13 and words[5] == "_do_write_small" and words[8] == "head" and words[11] == "tail"):
              head = int(words[9], 16)
              tail = int(words[12], 16)
              if (head != 0 or tail != 0):
                 prbegin[words[2]] = words[0] + "-" + words[1]
          elif (wdlen > 8 and words[5] == "_do_write_small" and words[7] == "deferred" and words[8] == "write"):
              if prbegin.has_key(words[2]):
                 endtime = words[0] + "-" + words[1]
                 prlat.append((prbegin[words[2]], (timestamp(endtime) - timestamp(prbegin[words[2]])).total_seconds()))
                 del prbegin[words[2]]   	    
          elif (wdlen > 10 and words[6] == "dequeue_op" and words[8] == "prio"):
              dqbegin[words[2]] = (words[0] + "-" + words[1], words[13], words[14])
          elif (wdlen == 9 and words[6] == "dequeue_op"):
              if dqbegin.has_key(words[2]):
                 endtime = words[0] + "-" + words[1]
                 dqlat.append((dqbegin[words[2]][0], (timestamp(endtime) - timestamp(dqbegin[words[2]][0])).total_seconds(), dqbegin[words[2]][1], dqbegin[words[2]][2]))
                 del dqbegin[words[2]]
 
  cnt = 1000
  dqlat.sort(key = lambda x : x[1], reverse = True)
  print "------------------------------Bluestore sort dequeue op by latency--------------------------"
  print "StartTime", "          dequeue Latency", "   queue latency", "op"
  for x in dqlat:
    if cnt > 0 :
       cnt -= 1
       print x[0], x[1], x[2], x[3]

  cnt = 10
  prlat.sort(key = lambda x : x[1], reverse = True)
  print "------------------------------Bluestore Penalty read sorted by latency--------------------------"
  print "StartTime", "          Latency"
  for x in prlat:
    if cnt > 0 :
       cnt -= 1
       print x[0], x[1]
 
  cnt = 10
  wlat.sort(key = lambda x : x[1], reverse = True)
  print "------------------------------Bluestore Writes sorted by latency--------------------------"
  print "Aligned", "       StartTime", "        Latency", "  Off~Len", "   Object"
  for x in wlat:
    if cnt > 0 :
       cnt -= 1
       print isAligned(x[2], 4096), x[0], x[1], x[2], x[3]
    
  cnt = 10           
  rlat.sort(key = lambda x : x[1], reverse = True)
  print "------------------------------Bluestore read sorted by latency--------------------------"
  print "Aligned", "       StartTime", "        Latency", "  Off~Len", "   Object"
  for x in rlat:
    if cnt > 0 :
       cnt -= 1
       print isAligned(x[2], 4096), x[0], x[1], x[2], x[3]
 
if __name__ == '__main__':
   main()
'''
