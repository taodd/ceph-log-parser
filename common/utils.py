# Copyright 2020-2021 Canonical Limited.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
import sys
import os
import time
import datetime

import re

def is_aligned(str, align):
     ### str format is offset~len
     p = str.index("~")
     offset = int(str[:p], 16)
     len = int(str[p+1:], 16)
     end = offset + len
     if (offset % align == 0 and end % align == 0):
        return True
     else:
        return False

def get_offset(str):
    ### str format is offset~len
    p = str.index("~")
    return int(str[:p], 16)

def get_len(str):
    ### str format is offset~len
    p = str.index("~")
    return int(str[p+1:], 16)

def timestamp(x):
   xstamp = datetime.datetime.strptime(x, "%Y-%m-%d-%H:%M:%S.%f")
   return xstamp

def time_substract(a, b):
   return (timestamp(a) - timestamp(b)).total_seconds()

def isAligned(str, align):
     p = str.index("~")
     offset = int(str[:p], 16)
     len = int(str[p+1:], 16)
     end = offset + len
     if (offset % align == 0 and end % align == 0):
        return True
     else:
        return False

def log_compare(words, strtpl, lst):
    if len(words) != len(strtpl):
       return False
    for idx in lst:
       if words[idx] != strtpl[idx]:
          return False
    return True

def log_match(logstr, elst):
    for e in elst:
       if re.search(e, logstr) == None:
          return False
    return True

def re_match(str, e):
   return re.search(e, str) != None

def log_compare_without_len(words, strtpl, lst):
    for idx in lst:
       if idx >= len(words) or words[idx] != strtpl[idx]:
          return False
    return True


def log_split(line):
    words = line.strip().split()
    return words

def gen_kv_list(dic):
    x = []
    y = []
    for k in dic.keys():
      x.append(k)
      y.append(dic[k])
    return x, y

def gen_k_list(dic):
   x = []
   for k in dic.keys():
     x.append(k)
   return x

def gen_v_list(dic):
   y = []
   for k in dic.keys():
     y.append(dic[k])
   return y


def gen_element_in_diclist(diclist, key):
  return [dic[key] for dic in diclist]

# with -1 as the debug level, usually print by lderr, like below
# 2016-12-20 20:37:23.059442 7fc313805800 -1 filestore(/var/lib/ceph/osd/ceph-38) mount failed to open journal /var/lib/ceph/osd/ceph-38/journal: (22) Invalid argument
errors = []

def check_err_log(words, line):
    if is_lderr_log(words):
       errors.append(line)

def is_lderr_log(words):
    value = 0
    try:
       value = int(words[3])
    except ValueError:
       pass
    return value < 0
def dump_errors():
   for err in errors:
      print(err)


def timestamp(x):
   xstamp = datetime.datetime.strptime(x, "%Y-%m-%d-%H:%M:%S.%f")

   return xstamp
