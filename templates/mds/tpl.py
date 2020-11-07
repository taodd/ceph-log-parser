import common.utils as utils

### mds cache stats || debug_mds 2###
cache_stats_log = "2020-08-31 07:09:19.141 7fe4a4b8f700  2 mds.0.cache Memory usage:  total 15075176, rss 14665904, heap 330416, baseline 330416, 3181526 / 3662455 inodes have caps, 3183808 caps, 0.86931 caps per inode"

#(0, '2020-08-31') (1, '07:09:19.141') (2, '7fe4a4b8f700') (3, '2') (4, 'mds.0.cache') (5, 'Memory') (6, 'usage:') (7, 'total') (8, '15075176,') (9, 'rss') (10, '14665904,') (11, 'heap') (12, '330416,') (13, 'baseline') (14, '330416,') (15, '3181526') (16, '/') (17, '3662455') (18, 'inodes') (19, 'have') (20, 'caps,') (21, '3183808') (22, 'caps,') (23, '0.86931') (24, 'caps') (25, 'per') (26, 'inode')

cache_stats_index_list = [5, 6, 18, 19, 20]

cache_stats_key2idx = {"timestamp" : 1, "rss" : 10, "inodes" : 17, "caps" : 21, "caps per inode" : 23}

cache_stats_words = utils.log_split(cache_stats_log)


### client not releasing caps || debug_mds 2 ###
not_releasing_caps_log = "2020-08-31 06:36:19.192 7fe4a6b93700  2 mds.beacon.juju-0f7010-18-lxd-0 Session stha8p0pq (3435558) is not releasing caps fast enough. Recalled caps at 33945 > 32768 (mds_recall_warning_threshold)."















