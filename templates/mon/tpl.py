
'''
1. osd failure report
2. monitor flapping
3. slow requests
'''

import common.utils as utils

### osd failure report | default log ###
osd_fail_log = "2020-04-09 22:31:07.432799 mon.juju-0aa49a-8-lxd-0 mon.0 10.10.0.84:6789/0 5487342 : cluster [DBG] osd.45 10.10.0.37:6800/511440 reported failed by osd.86 10.10.0.47:6803/5068"

#(0, '2020-04-09') (1, '22:31:07.432799') (2, 'mon.juju-0aa49a-8-lxd-0') (3, 'mon.0') (4, '10.10.0.84:6789/0') (5, '5487342') (6, ':') (7, 'cluster') (8, '[DBG]') (9, 'osd.45') (10, '10.10.0.37:6800/511440') (11, 'reported') (12, 'failed') (13, 'by') (14, 'osd.86') (15, '10.10.0.47:6803/5068')

osd_fail_index_list = [11, 12, 13]

osd_fail_key2idx = {"failed" : 9, "reporter" : 14 }

osd_fail_words = utils.log_split(osd_fail_log)


### monitor re-election ###
mon_flap_log = "2020-05-30 08:00:56.890317 mon.juju-e71ac3-7-lxd-0 mon.2 172.26.234.31:6789/0 250660 : cluster [INF] mon.juju-e71ac3-7-lxd-0 calling monitor election"

#(0, '2020-05-30') (1, '08:00:56.890317') (2, 'mon.juju-e71ac3-7-lxd-0') (3, 'mon.2') (4, '172.26.234.31:6789/0') (5, '250660') (6, ':') (7, 'cluster') (8, '[INF]') (9, 'mon.juju-e71ac3-7-lxd-0') (10, 'calling') (11, 'monitor') (12, 'election')

mon_flap_index_list = [10, 11, 12]

mon_flap_key2idx = {"mon" : 9}

mon_flap_words = utils.log_split(mon_flap_log)

### Slow requests
slow_requests = "2020-05-28 21:24:08.804634 mon.juju-e71ac3-18-lxd-4 mon.0 172.26.234.21:6789/0 5336 : cluster [WRN] Health check failed: 7 slow requests are blocked > 32 sec. Implicated osds 6 (REQUEST_SLOW)"
slow_requests_match_list = ["slow requests"]

### Network fault
net_fault = "2019-12-08 17:05:13.657946 7f23414a2700 0 -- 10.35.105.64:6789/0 >> 10.35.105.63:6789/0 conn(0x564e9bb2a000 :-1 s=STATE_OPEN pgs=79849 cs=5191 l=0).fault initiating reconnect"
