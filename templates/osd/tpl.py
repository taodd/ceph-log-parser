import common.utils as utils


bs_write_begin = "2020-06-01 08:48:53.059625 7fddaf6e4700 15 bluestore(/home/ubuntu/backport/luminous/ceph/build/dev/osd0) _write 7.4_head #7:24f7b562:::rbd_data.10606b8b4567.000000000000002f:head# 0x340c00~c00"

bs_write_end = "2020-06-01 08:48:53.059972 7fddaf6e4700 10 bluestore(/home/ubuntu/backport/luminous/ceph/build/dev/osd0) _write 7.4_head #7:24f7b562:::rbd_data.10606b8b4567.000000000000002f:head# 0x340c00~c00 = 0"

'''
(0, '2020-06-01') (1, '08:48:53.059625') (2, '7fddaf6e4700') (3, '15') (4, 'bluestore(/home/ubuntu/backport/luminous/ceph/build/dev/osd0)') (5, '_write') (6, '7.4_head') (7, '#7:24f7b562:::rbd_data.10606b8b4567.000000000000002f:head#') (8, '0x340c00~c00') 

(0, '2020-06-01') (1, '08:48:53.059972') (2, '7fddaf6e4700') (3, '10') (4, 'bluestore(/home/ubuntu/backport/luminous/ceph/build/dev/osd0)') (5, '_write') (6, '7.4_head') (7, '#7:24f7b562:::rbd_data.10606b8b4567.000000000000002f:head#') (8, '0x340c00~c00') (9, '=') (10, '0') 

'''
bs_write_begin_words = utils.log_split(bs_write_begin)
bs_write_end_words = utils.log_split(bs_write_end)

bs_write_bi_list = [5]
bs_write_ei_list = [5]

bs_write_begin_key2idx = {"thread": 2, "offlen": 8, "cid": 6, "oid": 7}
bs_write_end_key2idx = {"thread": 2, "offlen": 8, "cid": 6, "oid": 7}




bs_read_begin = "2020-06-01 08:48:05.909551 7fddb0ee7700 15 bluestore(/home/ubuntu/backport/luminous/ceph/build/dev/osd0) read 7.6_head #7:64243b03:::rbd_object_map.10606b8b4567:head# 0x12~80"

bs_read_end = "2020-06-01 08:48:05.909610 7fddb0ee7700 10 bluestore(/home/ubuntu/backport/luminous/ceph/build/dev/osd0) read 7.6_head #7:64243b03:::rbd_object_map.10606b8b4567:head# 0x12~80 = 128"
'''
(0, '2020-06-01') (1, '08:48:05.909551') (2, '7fddb0ee7700') (3, '15') (4, 'bluestore(/home/ubuntu/backport/luminous/ceph/build/dev/osd0)') (5, 'read') (6, '7.6_head') (7, '#7:64243b03:::rbd_object_map.10606b8b4567:head#') (8, '0x12~80') 

(0, '2020-06-01') (1, '08:48:05.909610') (2, '7fddb0ee7700') (3, '10') (4, 'bluestore(/home/ubuntu/backport/luminous/ceph/build/dev/osd0)') (5, 'read') (6, '7.6_head') (7, '#7:64243b03:::rbd_object_map.10606b8b4567:head#') (8, '0x12~80') (9, '=') (10, '128')
'''
bs_read_begin_words = utils.log_split(bs_read_begin)

bs_read_end_words = utils.log_split(bs_read_end)

bs_read_bi_list = [5]
bs_read_ei_list = [5]


bs_read_begin_key2idx = {"thread": 2, "offlen": 8, "cid": 6, "oid": 7}
bs_read_end_key2idx = {"thread": 2, "offlen": 8, "cid": 6, "oid": 7}


bs_penalty_read_begin = "2020-06-01 08:48:05.910972 7fddb0ee7700 20 bluestore(/home/ubuntu/backport/luminous/ceph/build/dev/osd0) _do_write_small  reading head 0x12 and tail 0x0"

bs_penalty_read_end = "2020-06-01 08:48:05.911065 7fddb0ee7700 20 bluestore(/home/ubuntu/backport/luminous/ceph/build/dev/osd0) _do_write_small  deferred write 0x0~1000 of mutable Blob(0x559a8051e6f0 blob([0x7c0000~10000] csum+has_unused crc32c/0x1000 unused=0xfffe) use_tracker(0x10000 0xa2) SharedBlob(0x559a8051ea00 sbid 0x0)) at [0x7c0000~1000]"

'''
(0, '2020-06-01') (1, '08:48:05.910972') (2, '7fddb0ee7700') (3, '20') (4, 'bluestore(/home/ubuntu/backport/luminous/ceph/build/dev/osd0)') (5, '_do_write_small') (6, 'reading') (7, 'head') (8, '0x12') (9, 'and') (10, 'tail') (11, '0x0') 

(0, '2020-06-01') (1, '08:48:05.911065') (2, '7fddb0ee7700') (3, '20') (4, 'bluestore(/home/ubuntu/backport/luminous/ceph/build/dev/osd0)') (5, '_do_write_small') (6, 'deferred') (7, 'write') (8, '0x0~1000') (9, 'of') (10, 'mutable') (11, 'Blob(0x559a8051e6f0') (12, 'blob([0x7c0000~10000]') (13, 'csum+has_unused') (14, 'crc32c/0x1000') (15, 'unused=0xfffe)') (16, 'use_tracker(0x10000') (17, '0xa2)') (18, 'SharedBlob(0x559a8051ea00') (19, 'sbid') (20, '0x0))') (21, 'at') (22, '[0x7c0000~1000]') 
'''

bs_pr_begin_words = utils.log_split(bs_penalty_read_begin)
bs_pr_bi_list = [5, 6, 7, 10]

### this should be without length
bs_pr_end_words = utils.log_split(bs_penalty_read_end)
bs_pr_ei_list = [5, 6, 7]

bs_pr_begin_key2idx = {"thread": 2, "head": 8, "tail": 11}
bs_pr_end_key2idx = {"thread": 2}

enqueue_op = "2020-10-06 10:59:01.430373 7fecfe40d700 15 osd.1 44 enqueue_op 0x55f1c2977a40 prio 63 cost 6245 latency 0.000192 epoch 44 osd_op(client.4135.0:1 1.7 1.217cd0df (undecoded) ondisk+write+known_if_redirected e44) v"

'''
(0, '2020-10-06') (1, '10:59:01.430373') (2, '7fecfe40d700') (3, '15') (4, 'osd.1') (5, '44') (6, 'enqueue_op') (7, '0x55f1c2977a40') (8, 'prio') (9, '63') (10, 'cost') (11, '6245') (12, 'latency') (13, '0.000192') (14, 'epoch') (15, '44') (16, 'osd_op(client.4135.0:1') (17, '1.7') (18, '1.217cd0df') (19, '(undecoded)') (20, 'ondisk+write+known_if_redirected') (21, 'e44)') (22, 'v') 
'''
enqueue_op_words = utils.log_split(enqueue_op)
enqueue_op_idx_list = [6, 8, 10]
enqueue_op_key2idx = {"opid" : 16, "before_enqueue_lat" : 13, "opref" : 7}

dequeue_op_start = "2020-10-06 10:59:01.430616 7fecde420700 10 osd.1 44 dequeue_op 0x55f1c2977a40 prio 63 cost 6245 latency 0.000435 osd_op(client.4135.0:1 1.7 1.217cd0df (undecoded) ondisk+write+known_if_redirected e44) v8 pg pg[1.7( empty local-lis/les=14/15 n=0 ec=14/14 lis/c 14/14 les/c/f 15/18/0 14/14/14) [1,3,0] r=0 lpr=14 crt=0'0 mlcod 0'0 active+clean]"
'''
(0, '2020-10-06') (1, '10:59:01.430616') (2, '7fecde420700') (3, '10') (4, 'osd.1') (5, '44') (6, 'dequeue_op') (7, '0x55f1c2977a40') (8, 'prio') (9, '63') (10, 'cost') (11, '6245') (12, 'latency') (13, '0.000435') (14, 'osd_op(client.4135.0:1') (15, '1.7') (16, '1.217cd0df') (17, '(undecoded)') (18, 'ondisk+write+known_if_redirected') (19, 'e44)') (20, 'v8') (21, 'pg') (22, 'pg[1.7(') (23, 'empty') (24, 'local-lis/les=14/15') (25, 'n=0') (26, 'ec=14/14') (27, 'lis/c') (28, '14/14') (29, 'les/c/f') (30, '15/18/0') (31, '14/14/14)') (32, '[1,3,0]') (33, 'r=0') (34, 'lpr=14') (35, "crt=0'0") (36, 'mlcod') (37, "0'0") (38, 'active+clean]') 
'''
dequeue_op_start_words = utils.log_split(dequeue_op_start)
dequeue_op_start_idx_list = [6, 8, 10, 12]
dequeue_op_start_key2idx = {"thread" : 2, "opid" : 14, "before_dequeue_lat" : 12, "opref": 7}

dequeue_op_end = "2020-10-08 13:57:07.426221 7fb2e9ee3700 10 osd.0 29 dequeue_op 0x55f43b9696c0 finish"
#(0, '2020-10-08') (1, '13:57:07.426221') (2, '7fb2e9ee3700') (3, '10') (4, 'osd.0') (5, '29') (6, 'dequeue_op') (7, '0x55f43b9696c0') (8, 'finish')
dequeue_op_end_words = utils.log_split(dequeue_op_end)
dequeue_op_end_idx_list = [6, 8]
dequeue_op_end_key2idx = {"thread": 2}

op_reply = "2020-10-06 10:59:01.612451 7fecf344a700 10 osd.1 pg_epoch: 44 pg[1.7( v 44'1 (0'0,44'1] local-lis/les=14/15 n=1 ec=14/14 lis/c 14/14 les/c/f 15/18/0 14/14/14) [1,3,0] r=0 lpr=14 lua=0'0 crt=44'1 lcod 0'0 mlcod 0'0 active+clean]  sending reply on osd_op(client.4135.0:1 1.7 1:fb0b3e84:::cephconf:head [writefull 0~6245] snapc 0=[] ondisk+write+known_if_redirected e44) v8 0x55f1c24616c0"
op_reply_match_list = ["sending reply on"]
op_reply_key = "osd_op\\(client"
op_reply_key2idx = {}
op_key = "osd_op"

subop = "2020-10-08 13:58:49.772065 7fb2e7edf700  1 -- 192.168.0.104:6802/2099 --> 192.168.0.104:6806/2415 -- osd_repop(client.4129.0:8373 7.4 e29/25 7:21acd049:::rbd_data.101f6b8b4567.00000000000000a7:head v 29'80) v2 -- 0x55f43c0c9100 con 0"
#(0, '2020-10-08') (1, '13:58:49.772065') (2, '7fb2e7edf700') (3, '1') (4, '--') (5, '192.168.0.104:6802/2099') (6, '-->') (7, '192.168.0.104:6806/2415') (8, '--') (9, 'osd_repop(client.4129.0:8373') (10, '7.4') (11, 'e29/25') (12, '7:21acd049:::rbd_data.101f6b8b4567.00000000000000a7:head') (13, 'v') (14, "29'80)") (15, 'v2') (16, '--') (17, '0x55f43c0c9100') (18, 'con') (19, '0') 
subop_words = utils.log_split(subop)
subop_idx_list = [3, 4, 6, 8]
subop_key2idx = {"dst" : 7, "subop_id": 9}
subop_match_list = ["osd_repop\\(client\\."]

subop_reply = "2020-10-08 13:58:49.867004 7fb3056c7700  1 -- 192.168.0.104:6802/2099 <== osd.1 192.168.0.104:6806/2415 6452 ==== osd_repop_reply(client.4125.0:5805 6.7 e29/22) v2 ==== 111+0+0 (2006894030 0 0) 0x55f43ccd3200 con 0x55f4391ba000"
#(0, '2020-10-08') (1, '13:58:49.867004') (2, '7fb3056c7700') (3, '1') (4, '--') (5, '192.168.0.104:6802/2099') (6, '<==') (7, 'osd.1') (8, '192.168.0.104:6806/2415') (9, '6452') (10, '====') (11, 'osd_repop_reply(client.4125.0:5805') (12, '6.7') (13, 'e29/22)') (14, 'v2') (15, '====') (16, '111+0+0') (17, '(2006894030') (18, '0') (19, '0)') (20, '0x55f43ccd3200') (21, 'con') (22, '0x55f4391ba000') 
subop_reply_words = utils.log_split(subop_reply)
subop_reply_idx_list = [3, 4, 6, 10]
subop_reply_key2idx = {"src": 8, "subosd": 7, "subop_reply_id": 11} #this dst should be src
subop_reply_match_list = ["osd_repop_reply\\(client\\."]

read_op = "2020-10-08 13:52:30.307364 7fb3056c7700  1 -- 192.168.0.104:6801/2099 <== client.4120 192.168.0.104:0/3784280633 23 ==== osd_op(client.4120.0:77 4.6 4.f8c99aee (undecoded) ondisk+read+known_if_redirected e23) v8 ==== 217+0+584 (38621151 0 4184362872) 0x55f438e0dd40 con 0x55f43b362800"
#(0, '2020-10-08') (1, '13:52:30.307364') (2, '7fb3056c7700') (3, '1') (4, '--') (5, '192.168.0.104:6801/2099') (6, '<==') (7, 'client.4120') (8, '192.168.0.104:0/3784280633') (9, '23') (10, '====') (11, 'osd_op(client.4120.0:77') (12, '4.6') (13, '4.f8c99aee') (14, '(undecoded)') (15, 'ondisk+read+known_if_redirected') (16, 'e23)') (17, 'v8') (18, '====') (19, '217+0+584') (20, '(38621151') (21, '0') (22, '4184362872)') (23, '0x55f438e0dd40') (24, 'con') (25, '0x55f43b362800')
read_op_words = utils.log_split(read_op)
read_op_idx_list = [3, 4, 6, 10]
read_op_match_list = ["osd_op\\(client\\.", "\\+read\\+"]
read_op_key2idx = {"src" : 8, "opid": 11}

ms_op_reply = "2020-10-08 13:52:30.308457 7fb2e96e2700  1 -- 192.168.0.104:6801/2099 --> 192.168.0.104:0/3784280633 -- osd_op_reply(77 notify.3 [notify cookie 94356280669904] v0'0 uv1 ondisk = 0) v8 -- 0x55f43b6376c0 con 0"
#(0, '2020-10-08') (1, '13:52:30.308457') (2, '7fb2e96e2700') (3, '1') (4, '--') (5, '192.168.0.104:6801/2099') (6, '-->') (7, '192.168.0.104:0/3784280633') (8, '--') (9, 'osd_op_reply(77') (10, 'notify.3') (11, '[notify') (12, 'cookie') (13, '94356280669904]') (14, "v0'0") (15, 'uv1') (16, 'ondisk') (17, '=') (18, '0)') (19, 'v8') (20, '--') (21, '0x55f43b6376c0') (22, 'con') (23, '0') 
ms_op_reply_words = utils.log_split(op_reply)
ms_op_reply_idx_list = [3, 4, 6, 8]
ms_op_reply_match_list = ["osd_op_reply\\(\d"]
ms_op_reply_key2idx = {"dst": 7, "reply_id": 9}

#op_commit.time - eval_repop.time = bluestore time
eval_repop = "2020-10-08 13:58:46.638131 7fb2e8ee1700 10 osd.0 pg_epoch: 29 pg[7.25( v 29'63 (0'0,29'63] local-lis/les=25/26 n=2 ec=25/25 lis/c 25/25 les/c/f 26/26/0 25/25/25) [0,1,2] r=0 lpr=25 luod=29'62 lua=29'62 crt=29'63 lcod 29'61 mlcod 29'61 active+clean] eval_repop repgather(0x55f43c9da100 29'63 rep_tid=3441 committed?=0 applied?=0 r=0)"
eval_repop_words = utils.log_split(eval_repop)
eval_repop_match_list = ["eval_repop repgather\\("]
eval_repop_key2idx = {"thread": 2, "rep_tid": -4}

op_commit = "2020-10-08 13:58:46.614357 7fb2f66fc700 10 osd.0 pg_epoch: 29 pg[7.6( v 29'149 (0'0,29'149] local-lis/les=25/26 n=8 ec=25/25 lis/c 25/25 les/c/f 26/26/0 25/25/25) [0,2,1] r=0 lpr=25 luod=29'147 lua=29'147 crt=29'149 lcod 29'146 mlcod 29'146 active+clean] op_commit: 3433"
op_commit_words = utils.log_split(op_commit)
op_commit_idx_list = [5, -2]
op_commit_key2idx = {"rep_tid": -1}



