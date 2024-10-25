#!/usr/bin/env python3
# -*-coding=utf-8-*-
#
# Copyright (C) 2024, Rockchip Electronics Co., Ltd.
#

import os
import re
import sys
import copy
import getopt
import platform
import struct
from datetime import datetime

version_max = 5
update_key_list = []

chip_info = 'null'
chip_list = ['px30', 'px30s', 'px3se', 'px5', 'rk1808', 'rk2118', 'rk312x', 'rk3126', 'rk3128',
    'rk3128h', 'rk322x', 'rk3228a', 'rk3228b', 'rk3228h', 'rk322xh', 'rk3229', 'rk3308', 'rk3288',
    'rk3326', 'rk3326s', 'rk3328', 'rk3368', 'rk3399', 'rk3506', 'rk3528', 'rk356x', 'rk3562',
    'rk3566', 'rk3568', 'rk3576', 'rk3588', 'rv1103', 'rv1103b', 'rv1106', 'rv1108', 'rv1109',
    'rv1126']

version_old_list = ['rk322xh', 'rk3328', 'rk3318']

# struct rk3528_ca_skew
rk3528_ca_skew = {
    'skew_freq': 0,
    'ca_skew_0': 0,
    'ca_skew_1': 0,
    'ca_skew_2': 0,
    'ca_skew_3': 0,
    'ca_skew_4': 0,
    'ca_skew_5': 0,
    'ca_skew_6': 0,
    'ca_skew_7': 0,
}

# struct rk3528_skew_info
rk3528_skew_info = {
    'skew_sub_version': 0,
    'ddr3' : rk3528_ca_skew.copy(),
    'ddr4' : rk3528_ca_skew.copy(),
    'lp3' : rk3528_ca_skew.copy(),
}

# struct index_info, u8
index_info = {
    'offset' : 0,
    'size' : 0
}

# struct sdram_head_info_index_v2
sdram_head_info_index_v2 = {
    'cpu_gen_index' : index_info.copy(),
    'global_index' : index_info.copy(),
    'ddr2_index' : index_info.copy(),
    'ddr3_index' : index_info.copy(),
    'ddr4_index' : index_info.copy(),
    'ddr5_index' : index_info.copy(),
    'lp2_index' : index_info.copy(),
    'lp3_index' : index_info.copy(),
    'lp4_index' : index_info.copy(),
    'lp5_index' : index_info.copy(),
    'skew_index' : index_info.copy(),
    'dq_map_index' : index_info.copy(),
}

sdram_head_info_index_v2_3 = {
    'lp4x_index' : index_info.copy(),
    'lp4_4x_hash_index' : index_info.copy()
}

sdram_head_info_index_v3_4 = {
    'lp5_hash_index' : index_info.copy(),
    'ddr4_hash_index' : index_info.copy(),
    'lp3_hash_index' : index_info.copy(),
    'ddr3_hash_index' : index_info.copy(),
    'lp2_hash_index' : index_info.copy(),
    'ddr2_hash_index' : index_info.copy(),
    'ddr5_hash_index' : index_info.copy(),
}

# struct global_info
global_info = {
    'uart_info' : 0,
    'sr_pd_info' : 0,
    'ch_info' : 0,
    'info_2t' : 0,
    'reserved_0' : 0,
    'reserved_1' : 0,
    'reserved_2' : 0,
    'reserved_3' : 0,
}

# struct ddr2_3_4_lp2_3_info
ddr2_3_4_lp2_3_info = {
    'ddr_freq0_1' : 0,
    'ddr_freq2_3' : 0,
    'ddr_freq4_5' : 0,
    'drv_when_odten' : 0,
    'drv_when_odtoff' : 0,
    'odt_info' : 0,
    'odten_freq' : 0,
    'sr_when_odten' : 0,
    'sr_when_odtoff' : 0,
}

# struct ddr2_3_4_lp2_3_info_v5
ddr2_3_4_lp2_3_info_v5 = {
    'ddr_freq0_1' : 0,
    'ddr_freq2_3' : 0,
    'ddr_freq4_5' : 0,
    'drv_when_odten' : 0,
    'drv_when_odtoff' : 0,
    'odt_info' : 0,
    'odten_freq' : 0,
    'sr_when_odten' : 0,
    'sr_when_odtoff' : 0,
    'vref_when_odten' : 0,
    'vref_when_odtoff' : 0,
}

# struct lp4_info
lp4_info = {
    'ddr_freq0_1' : 0,
    'ddr_freq2_3' : 0,
    'ddr_freq4_5' : 0,
    'drv_when_odten' : 0,
    'drv_when_odtoff' : 0,
    'odt_info' : 0,
    'dq_odten_freq' : 0,
    'sr_when_odten' : 0,
    'sr_when_odtoff' : 0,
    'ca_odten_freq' : 0,
    'cs_drv_ca_odt_info' : 0,
    'vref_when_odten' : 0,
    'vref_when_odtoff' : 0,
}

# struct dq_map_info
dq_map_info = {
    'byte_map_0' : 0,
    'byte_map_1' : 0,
    'lp3_dq0_7_map' : 0,
    'lp2_dq0_7_map' : 0,
    'ddr4_dq_map_0' : 0,
    'ddr4_dq_map_1' : 0,
    'ddr4_dq_map_2' : 0,
    'ddr4_dq_map_3' : 0,
}

# struct hash_info
hash_info = {
    'ch_mask_0' : 0,
    'ch_mask_1' : 0,
    'bank_mask_0' : 0,
    'bank_mask_1' : 0,
    'bank_mask_2' : 0,
    'bank_mask_3' : 0,
    'rank_mask0' : 0,
    'rank_mask1' : 0,
}

# struct sdram_head_info_v2
sdram_head_info_v2 = {
    'global_info' : global_info.copy(),
    'ddr2_info' : ddr2_3_4_lp2_3_info.copy(),
    'ddr3_info' : ddr2_3_4_lp2_3_info.copy(),
    'ddr4_info' : ddr2_3_4_lp2_3_info.copy(),
    'ddr5_info' : ddr2_3_4_lp2_3_info.copy(),
    'lp2_info' : ddr2_3_4_lp2_3_info.copy(),
    'lp3_info' : ddr2_3_4_lp2_3_info.copy(),
    'lp4_info' : lp4_info.copy(),
    'dq_map_info' : dq_map_info.copy(),
    'lp4x_info' : lp4_info.copy(),
    'lp5_info' : lp4_info.copy(),
    'lp4_4x_hash_info' : hash_info.copy(),
    'lp5_hash_info' : hash_info.copy(),
    'ddr4_hash_info' : hash_info.copy(),
    'lp3_hash_info' : hash_info.copy(),
    'ddr3_hash_info' : hash_info.copy(),
    'lp2_hash_info' : hash_info.copy(),
    'ddr2_hash_info' : hash_info.copy(),
    'ddr5_hash_info' : hash_info.copy(),
}

# struct sdram_head_info_v5
sdram_head_info_v5 = {
    'global_info' : global_info.copy(),
    'ddr2_info' : ddr2_3_4_lp2_3_info_v5.copy(),
    'ddr3_info' : ddr2_3_4_lp2_3_info_v5.copy(),
    'ddr4_info' : ddr2_3_4_lp2_3_info_v5.copy(),
    'ddr5_info' : ddr2_3_4_lp2_3_info_v5.copy(),
    'lp2_info' : ddr2_3_4_lp2_3_info_v5.copy(),
    'lp3_info' : ddr2_3_4_lp2_3_info_v5.copy(),
    'lp4_info' : lp4_info.copy(),
    'dq_map_info' : dq_map_info.copy(),
    'lp4x_info' : lp4_info.copy(),
    'lp5_info' : lp4_info.copy(),
    'lp4_4x_hash_info' : hash_info.copy(),
    'lp5_hash_info' : hash_info.copy(),
    'ddr4_hash_info' : hash_info.copy(),
    'lp3_hash_info' : hash_info.copy(),
    'ddr3_hash_info' : hash_info.copy(),
    'lp2_hash_info' : hash_info.copy(),
    'ddr2_hash_info' : hash_info.copy(),
    'ddr5_hash_info' : hash_info.copy(),
}

sdram_head_info_v0 = [[0xc, 0], [0x10, 0], [0x14, 0], [0x18, 0], [0x1c, 0], [0x20, 0], [0x24, 0]]

# struct base_info_full
base_info_full = {
    'start tag': {'value': 0, 'num_base': 'hex', 'index': 'null', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 0, 'v0_info': [0x0, 0, 0xffffffff]},

    'ddr2_freq': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'ddr_freq0_1', 'shift': 0, 'mask': 0xfff, 'version': 0, 'v0_info': [0xc, 16, 0xffff]},
    'lp2_freq': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'ddr_freq0_1', 'shift': 0, 'mask': 0xfff, 'version': 0, 'v0_info': [0xc, 0, 0xffff]},
    'ddr3_freq': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'ddr_freq0_1', 'shift': 0, 'mask': 0xfff, 'version': 0, 'v0_info': [0x10, 16, 0xffff]},
    'lp3_freq': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'ddr_freq0_1', 'shift': 0, 'mask': 0xfff, 'version': 0, 'v0_info': [0x10, 0, 0xffff]},
    'ddr4_freq': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'ddr_freq0_1', 'shift': 0, 'mask': 0xfff, 'version': 0, 'v0_info': [0x14, 16, 0xffff]},
    'lp4_freq': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'ddr_freq0_1', 'shift': 0, 'mask': 0xfff, 'version': 0, 'v0_info': [0x14, 0, 0xffff]},
    'lp4x_freq': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'ddr_freq0_1', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'lp5_freq': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'ddr_freq0_1', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'uart id': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'uart_info', 'shift': 28, 'mask': 0xf, 'version': 0, 'v0_info': [0x18, 28, 0xf]},
    'uart iomux': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'uart_info', 'shift': 24, 'mask': 0xf, 'version': 0, 'v0_info': [0x18, 24, 0xf]},
    'uart baudrate': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'uart_info', 'shift': 0, 'mask': 0xffffff, 'version': 0, 'v0_info': [0x18, 0, 0xffffff]},
    'sr_idle': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'sr_pd_info', 'shift': 16, 'mask': 0xffff, 'version': 0, 'v0_info': [0x1c, 16, 0xffff]},
    'pd_idle': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'sr_pd_info', 'shift': 0, 'mask': 0xffff, 'version': 0, 'v0_info': [0x1c, 0, 0xffff]},
    'first scan channel': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'ch_info', 'shift': 28, 'mask': 0xf, 'version': 0, 'v0_info': [0x20, 28, 0xf]},
    'channel mask': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'ch_info', 'shift': 24, 'mask': 0xf, 'version': 0, 'v0_info': [0x20, 24, 0xf]},
    'stride type': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'ch_info', 'shift': 16, 'mask': 0xff, 'version': 0, 'v0_info': [0x20, 16, 0xff]},
    'standby_idle': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'ch_info', 'shift': 0, 'mask': 0xffff, 'version': 0, 'v0_info': [0x20, 0, 0xffff]},
    'ext_temp_ref': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'info_2t', 'shift': 29, 'mask': 0x3, 'version': 0, 'v0_info': [0x24, 29, 0x3]},
    'link_ecc_en': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'info_2t', 'shift': 28, 'mask': 0x1, 'version': 2},
    'per_bank_ref_en': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'info_2t', 'shift': 27, 'mask': 0x1, 'version': 2},
    'derate_en': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'info_2t', 'shift': 26, 'mask': 0x1, 'version': 0, 'v0_info': [0x24, 26, 0x1]},
    'auto_precharge_en': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'info_2t', 'shift': 25, 'mask': 0x1, 'version': 2},
    'res_space_remap_all': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'info_2t', 'shift': 24, 'mask': 0x1, 'version': 2},
    'res_space_remap_portion': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'info_2t', 'shift': 20, 'mask': 0x1, 'version': 2},
    'rd_vref_scan_en': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'info_2t', 'shift': 21, 'mask': 0x1, 'version': 2},
    'wr_vref_scan_en': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'info_2t', 'shift': 22, 'mask': 0x1, 'version': 2},
    'eye_2d_scan_en': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'info_2t', 'shift': 23, 'mask': 0x1, 'version': 2},
    'dis_train_print': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'info_2t', 'shift': 19, 'mask': 0x1, 'version': 2},
    'ssmod_downspread': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'info_2t', 'shift': 17, 'mask': 0x3, 'version': 0, 'v0_info': [0x24, 17, 0x3]},
    'ssmod_div': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'info_2t', 'shift': 9, 'mask': 0xff, 'version': 0, 'v0_info': [0x24, 9, 0xff]},
    'ssmod_spread': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'info_2t', 'shift': 1, 'mask': 0xff, 'version': 0, 'v0_info': [0x24, 1, 0xff]},
    'ddr_2t': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'info_2t', 'shift': 0, 'mask': 0x1, 'version': 0, 'v0_info': [0x24, 0, 0x1]},
    'reserved_global_info_2t_bit31': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'info_2t', 'shift': 31, 'mask': 0x1, 'version': 2},
    'pstore_base_addr': {'value': 0, 'num_base': 'hex', 'index': 'global_index', 'position': 'reserved_0', 'shift': 16, 'mask': 0xffff, 'version': 2},
    'pstore_buf_size': {'value': 0, 'num_base': 'hex', 'index': 'global_index', 'position': 'reserved_0', 'shift': 12, 'mask': 0xf, 'version': 2},
    'uboot_log_en': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'reserved_0', 'shift': 4, 'mask': 0x1, 'version': 2},
    'atf_log_en': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'reserved_0', 'shift': 3, 'mask': 0x1, 'version': 2},
    'optee_log_en': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'reserved_0', 'shift': 2, 'mask': 0x1, 'version': 2},
    'spl_log_en': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'reserved_0', 'shift': 1, 'mask': 0x1, 'version': 2},
    'tpl_log_en': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'reserved_0', 'shift': 0, 'mask': 0x1, 'version': 2},
    'reserved_global_reserved_0_bit5_11': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'reserved_0', 'shift': 5, 'mask': 0x7f, 'version': 2},
    'first_init_dram_type': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'reserved_1', 'shift': 5, 'mask': 0xf, 'version': 2},
    'dfs_disable': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'reserved_1', 'shift': 4, 'mask': 0x1, 'version': 2},
    'pageclose': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'reserved_1', 'shift': 3, 'mask': 0x1, 'version': 2},
    'boot_fsp': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'reserved_1', 'shift': 0, 'mask': 0x7, 'version': 2},
    'reserved_global_reserved_1_bit9_31': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'reserved_1', 'shift': 9, 'mask': 0x7fffff, 'version': 2},
    'reserved_global_reserved_2_bit0_31': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'reserved_2', 'shift': 0, 'mask': 0xffffffff, 'version': 2},
    'reserved_global_reserved_3_bit0_31': {'value': 0, 'num_base': 'dec', 'index': 'global_index', 'position': 'reserved_3', 'shift': 0, 'mask': 0xffffffff, 'version': 2},

    'ddr2_f1_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'ddr_freq0_1', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_ddr2_ddr_freq0_1_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'ddr_freq0_1', 'shift': 24, 'mask': 0xff, 'version': 2},
    'ddr2_f2_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'ddr_freq2_3', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'ddr2_f3_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'ddr_freq2_3', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_ddr2_ddr_freq2_3_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'ddr_freq2_3', 'shift': 24, 'mask': 0xff, 'version': 2},
    'ddr2_f4_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'ddr_freq4_5', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'ddr2_f5_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'ddr_freq4_5', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_ddr2_ddr_freq4_5_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'ddr_freq4_5', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_ddr2_dq_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'drv_when_odten', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_ddr2_ca_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'drv_when_odten', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_ddr2_clk_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'drv_when_odten', 'shift': 16, 'mask': 0xff, 'version': 2},
    'ddr2_dq_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'drv_when_odten', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_ddr2_dq_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'drv_when_odtoff', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_ddr2_ca_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'drv_when_odtoff', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_ddr2_clk_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'drv_when_odtoff', 'shift': 16, 'mask': 0xff, 'version': 2},
    'ddr2_dq_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'drv_when_odtoff', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_ddr2_odt_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'odt_info', 'shift': 8, 'mask': 0x3ff, 'version': 2},
    'ddr2_odt_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'odt_info', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_ddr2_odt_pull_up_en': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'odt_info', 'shift': 18, 'mask': 0x1, 'version': 2},
    'phy_ddr2_odt_pull_dn_en': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'odt_info', 'shift': 19, 'mask': 0x1, 'version': 2},
    'reserved_ddr2_odt_info_bit20_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'odt_info', 'shift': 20, 'mask': 0xfff, 'version': 2},
    'phy_ddr2_odten_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'odten_freq', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'ddr2_odten_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'odten_freq', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'reserved_ddr2_odten_freq_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'odten_freq', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_ddr2_dq_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'sr_when_odten', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_ddr2_ca_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'sr_when_odten', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_ddr2_clk_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'sr_when_odten', 'shift': 16, 'mask': 0xff, 'version': 2},
    'reserved_ddr2_sr_when_odten_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'sr_when_odten', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_ddr2_dq_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'sr_when_odtoff', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_ddr2_ca_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'sr_when_odtoff', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_ddr2_clk_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'sr_when_odtoff', 'shift': 16, 'mask': 0xff, 'version': 2},
    'reserved_ddr2_sr_when_odtoff_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'sr_when_odtoff', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_ddr2_dq_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'vref_when_odten', 'shift': 0, 'mask': 0x3ff, 'version': 5},
    'ddr2_dq_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'vref_when_odten', 'shift': 10, 'mask': 0x3ff, 'version': 5},
    'ddr2_ca_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'vref_when_odten', 'shift': 20, 'mask': 0x3ff, 'version': 5},
    'reserved_ddr2_vref_when_odten_bit30_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'vref_when_odten', 'shift': 30, 'mask': 0x3, 'version': 5},
    'phy_ddr2_dq_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'vref_when_odtoff', 'shift': 0, 'mask': 0x3ff, 'version': 5},
    'ddr2_dq_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'vref_when_odtoff', 'shift': 10, 'mask': 0x3ff, 'version': 5},
    'ddr2_ca_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'vref_when_odtoff', 'shift': 20, 'mask': 0x3ff, 'version': 5},
    'reserved_ddr2_vref_when_odtoff_bit30_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr2_index', 'position': 'vref_when_odtoff', 'shift': 30, 'mask': 0x3, 'version': 5},

    'ddr3_f1_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'ddr_freq0_1', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_ddr3_ddr_freq0_1_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'ddr_freq0_1', 'shift': 24, 'mask': 0xff, 'version': 2},
    'ddr3_f2_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'ddr_freq2_3', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'ddr3_f3_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'ddr_freq2_3', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_ddr3_ddr_freq2_3_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'ddr_freq2_3', 'shift': 24, 'mask': 0xff, 'version': 2},
    'ddr3_f4_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'ddr_freq4_5', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'ddr3_f5_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'ddr_freq4_5', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_ddr3_ddr_freq4_5_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'ddr_freq4_5', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_ddr3_dq_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'drv_when_odten', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_ddr3_ca_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'drv_when_odten', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_ddr3_clk_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'drv_when_odten', 'shift': 16, 'mask': 0xff, 'version': 2},
    'ddr3_dq_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'drv_when_odten', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_ddr3_dq_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'drv_when_odtoff', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_ddr3_ca_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'drv_when_odtoff', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_ddr3_clk_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'drv_when_odtoff', 'shift': 16, 'mask': 0xff, 'version': 2},
    'ddr3_dq_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'drv_when_odtoff', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_ddr3_odt_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'odt_info', 'shift': 8, 'mask': 0x3ff, 'version': 2},
    'ddr3_odt_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'odt_info', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_ddr3_odt_pull_up_en': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'odt_info', 'shift': 18, 'mask': 0x1, 'version': 2},
    'phy_ddr3_odt_pull_dn_en': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'odt_info', 'shift': 19, 'mask': 0x1, 'version': 2},
    'reserved_ddr3_odt_info_bit20_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'odt_info', 'shift': 20, 'mask': 0xfff, 'version': 2},
    'phy_ddr3_odten_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'odten_freq', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'ddr3_odten_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'odten_freq', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'reserved_ddr3_odten_freq_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'odten_freq', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_ddr3_dq_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'sr_when_odten', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_ddr3_ca_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'sr_when_odten', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_ddr3_clk_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'sr_when_odten', 'shift': 16, 'mask': 0xff, 'version': 2},
    'reserved_ddr3_sr_when_odten_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'sr_when_odten', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_ddr3_dq_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'sr_when_odtoff', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_ddr3_ca_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'sr_when_odtoff', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_ddr3_clk_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'sr_when_odtoff', 'shift': 16, 'mask': 0xff, 'version': 2},
    'reserved_ddr3_sr_when_odtoff_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'sr_when_odtoff', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_ddr3_dq_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'vref_when_odten', 'shift': 0, 'mask': 0x3ff, 'version': 5},
    'ddr3_dq_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'vref_when_odten', 'shift': 10, 'mask': 0x3ff, 'version': 5},
    'ddr3_ca_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'vref_when_odten', 'shift': 20, 'mask': 0x3ff, 'version': 5},
    'reserved_ddr3_vref_when_odten_bit30_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'vref_when_odten', 'shift': 30, 'mask': 0x3, 'version': 5},
    'phy_ddr3_dq_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'vref_when_odtoff', 'shift': 0, 'mask': 0x3ff, 'version': 5},
    'ddr3_dq_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'vref_when_odtoff', 'shift': 10, 'mask': 0x3ff, 'version': 5},
    'ddr3_ca_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'vref_when_odtoff', 'shift': 20, 'mask': 0x3ff, 'version': 5},
    'reserved_ddr3_vref_when_odtoff_bit30_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr3_index', 'position': 'vref_when_odtoff', 'shift': 30, 'mask': 0x3, 'version': 5},

    'ddr4_f1_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'ddr_freq0_1', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_ddr4_ddr_freq0_1_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'ddr_freq0_1', 'shift': 24, 'mask': 0xff, 'version': 2},
    'ddr4_f2_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'ddr_freq2_3', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'ddr4_f3_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'ddr_freq2_3', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_ddr4_ddr_freq2_3_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'ddr_freq2_3', 'shift': 24, 'mask': 0xff, 'version': 2},
    'ddr4_f4_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'ddr_freq4_5', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'ddr4_f5_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'ddr_freq4_5', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_ddr4_ddr_freq4_5_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'ddr_freq4_5', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_ddr4_dq_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'drv_when_odten', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_ddr4_ca_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'drv_when_odten', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_ddr4_clk_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'drv_when_odten', 'shift': 16, 'mask': 0xff, 'version': 2},
    'ddr4_dq_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'drv_when_odten', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_ddr4_dq_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'drv_when_odtoff', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_ddr4_ca_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'drv_when_odtoff', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_ddr4_clk_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'drv_when_odtoff', 'shift': 16, 'mask': 0xff, 'version': 2},
    'ddr4_dq_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'drv_when_odtoff', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_ddr4_odt_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'odt_info', 'shift': 8, 'mask': 0x3ff, 'version': 2},
    'ddr4_odt_ohm': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'odt_info', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_ddr4_odt_pull_up_en': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'odt_info', 'shift': 18, 'mask': 0x1, 'version': 2},
    'phy_ddr4_odt_pull_dn_en': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'odt_info', 'shift': 19, 'mask': 0x1, 'version': 2},
    'reserved_ddr4_odt_info_bit20_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'odt_info', 'shift': 20, 'mask': 0xfff, 'version': 2},
    'phy_ddr4_odten_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'odten_freq', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'ddr4_odten_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'odten_freq', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'reserved_ddr4_odten_freq_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'odten_freq', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_ddr4_dq_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'sr_when_odten', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_ddr4_ca_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'sr_when_odten', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_ddr4_clk_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'sr_when_odten', 'shift': 16, 'mask': 0xff, 'version': 2},
    'reserved_ddr4_sr_when_odten_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'sr_when_odten', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_ddr4_dq_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'sr_when_odtoff', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_ddr4_ca_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'sr_when_odtoff', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_ddr4_clk_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'sr_when_odtoff', 'shift': 16, 'mask': 0xff, 'version': 2},
    'reserved_ddr4_sr_when_odtoff_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'sr_when_odtoff', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_ddr4_dq_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'vref_when_odten', 'shift': 0, 'mask': 0x3ff, 'version': 5},
    'ddr4_dq_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'vref_when_odten', 'shift': 10, 'mask': 0x3ff, 'version': 5},
    'ddr4_ca_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'vref_when_odten', 'shift': 20, 'mask': 0x3ff, 'version': 5},
    'reserved_ddr4_vref_when_odten_bit30_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'vref_when_odten', 'shift': 30, 'mask': 0x3, 'version': 5},
    'phy_ddr4_dq_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'vref_when_odtoff', 'shift': 0, 'mask': 0x3ff, 'version': 5},
    'ddr4_dq_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'vref_when_odtoff', 'shift': 10, 'mask': 0x3ff, 'version': 5},
    'ddr4_ca_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'vref_when_odtoff', 'shift': 20, 'mask': 0x3ff, 'version': 5},
    'reserved_ddr4_vref_when_odtoff_bit30_31': {'value': 0, 'num_base': 'dec', 'index': 'ddr4_index', 'position': 'vref_when_odtoff', 'shift': 30, 'mask': 0x3, 'version': 5},

    'lp2_f1_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'ddr_freq0_1', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_lp2_ddr_freq0_1_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'ddr_freq0_1', 'shift': 24, 'mask': 0xff, 'version': 2},
    'lp2_f2_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'ddr_freq2_3', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'lp2_f3_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'ddr_freq2_3', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_lp2_ddr_freq2_3_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'ddr_freq2_3', 'shift': 24, 'mask': 0xff, 'version': 2},
    'lp2_f4_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'ddr_freq4_5', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'lp2_f5_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'ddr_freq4_5', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_lp2_ddr_freq4_5_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'ddr_freq4_5', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp2_dq_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'drv_when_odten', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp2_ca_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'drv_when_odten', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_lp2_clk_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'drv_when_odten', 'shift': 16, 'mask': 0xff, 'version': 2},
    'lp2_dq_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'drv_when_odten', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp2_dq_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'drv_when_odtoff', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp2_ca_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'drv_when_odtoff', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_lp2_clk_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'drv_when_odtoff', 'shift': 16, 'mask': 0xff, 'version': 2},
    'lp2_dq_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'drv_when_odtoff', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp2_odt_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'odt_info', 'shift': 8, 'mask': 0x3ff, 'version': 2},
    'lp2_odt_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'odt_info', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp2_odt_pull_up_en': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'odt_info', 'shift': 18, 'mask': 0x1, 'version': 2},
    'phy_lp2_odt_pull_dn_en': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'odt_info', 'shift': 19, 'mask': 0x1, 'version': 2},
    'reserved_lp2_odt_info_bit20_31': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'odt_info', 'shift': 20, 'mask': 0xfff, 'version': 2},
    'phy_lp2_odten_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'odten_freq', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'lp2_odten_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'odten_freq', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'reserved_lp2_odten_freq_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'odten_freq', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp2_dq_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'sr_when_odten', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp2_ca_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'sr_when_odten', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_lp2_clk_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'sr_when_odten', 'shift': 16, 'mask': 0xff, 'version': 2},
    'reserved_lp2_sr_when_odten_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'sr_when_odten', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp2_dq_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'sr_when_odtoff', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp2_ca_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'sr_when_odtoff', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_lp2_clk_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'sr_when_odtoff', 'shift': 16, 'mask': 0xff, 'version': 2},
    'reserved_lp2_sr_when_odtoff_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'sr_when_odtoff', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp2_dq_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'vref_when_odten', 'shift': 0, 'mask': 0x3ff, 'version': 5},
    'lp2_dq_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'vref_when_odten', 'shift': 10, 'mask': 0x3ff, 'version': 5},
    'lp2_ca_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'vref_when_odten', 'shift': 20, 'mask': 0x3ff, 'version': 5},
    'reserved_lp2_vref_when_odten_bit30_31': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'vref_when_odten', 'shift': 30, 'mask': 0x3, 'version': 5},
    'phy_lp2_dq_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'vref_when_odtoff', 'shift': 0, 'mask': 0x3ff, 'version': 5},
    'lp2_dq_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'vref_when_odtoff', 'shift': 10, 'mask': 0x3ff, 'version': 5},
    'lp2_ca_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'vref_when_odtoff', 'shift': 20, 'mask': 0x3ff, 'version': 5},
    'reserved_lp2_vref_when_odtoff_bit30_31': {'value': 0, 'num_base': 'dec', 'index': 'lp2_index', 'position': 'vref_when_odtoff', 'shift': 30, 'mask': 0x3, 'version': 5},

    'lp3_f1_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'ddr_freq0_1', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_lp3_ddr_freq0_1_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'ddr_freq0_1', 'shift': 24, 'mask': 0xff, 'version': 2},
    'lp3_f2_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'ddr_freq2_3', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'lp3_f3_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'ddr_freq2_3', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_lp3_ddr_freq2_3_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'ddr_freq2_3', 'shift': 24, 'mask': 0xff, 'version': 2},
    'lp3_f4_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'ddr_freq4_5', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'lp3_f5_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'ddr_freq4_5', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_lp3_ddr_freq4_5_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'ddr_freq4_5', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp3_dq_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'drv_when_odten', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp3_ca_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'drv_when_odten', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_lp3_clk_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'drv_when_odten', 'shift': 16, 'mask': 0xff, 'version': 2},
    'lp3_dq_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'drv_when_odten', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp3_dq_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'drv_when_odtoff', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp3_ca_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'drv_when_odtoff', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_lp3_clk_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'drv_when_odtoff', 'shift': 16, 'mask': 0xff, 'version': 2},
    'lp3_dq_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'drv_when_odtoff', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp3_odt_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'odt_info', 'shift': 8, 'mask': 0x3ff, 'version': 2},
    'lp3_odt_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'odt_info', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp3_odt_pull_up_en': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'odt_info', 'shift': 18, 'mask': 0x1, 'version': 2},
    'phy_lp3_odt_pull_dn_en': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'odt_info', 'shift': 19, 'mask': 0x1, 'version': 2},
    'reserved_lp3_odt_info_bit20_31': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'odt_info', 'shift': 20, 'mask': 0xfff, 'version': 2},
    'phy_lp3_odten_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'odten_freq', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'lp3_odten_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'odten_freq', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'reserved_lp3_odten_freq_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'odten_freq', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp3_dq_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'sr_when_odten', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp3_ca_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'sr_when_odten', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_lp3_clk_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'sr_when_odten', 'shift': 16, 'mask': 0xff, 'version': 2},
    'reserved_lp3_sr_when_odten_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'sr_when_odten', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp3_dq_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'sr_when_odtoff', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp3_ca_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'sr_when_odtoff', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_lp3_clk_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'sr_when_odtoff', 'shift': 16, 'mask': 0xff, 'version': 2},
    'reserved_lp3_sr_when_odtoff_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'sr_when_odtoff', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp3_dq_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'vref_when_odten', 'shift': 0, 'mask': 0x3ff, 'version': 5},
    'lp3_dq_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'vref_when_odten', 'shift': 10, 'mask': 0x3ff, 'version': 5},
    'lp3_ca_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'vref_when_odten', 'shift': 20, 'mask': 0x3ff, 'version': 5},
    'reserved_lp3_vref_when_odten_bit30_31': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'vref_when_odten', 'shift': 30, 'mask': 0x3, 'version': 5},
    'phy_lp3_dq_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'vref_when_odtoff', 'shift': 0, 'mask': 0x3ff, 'version': 5},
    'lp3_dq_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'vref_when_odtoff', 'shift': 10, 'mask': 0x3ff, 'version': 5},
    'lp3_ca_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'vref_when_odtoff', 'shift': 20, 'mask': 0x3ff, 'version': 5},
    'reserved_lp3_vref_when_odtoff_bit30_31': {'value': 0, 'num_base': 'dec', 'index': 'lp3_index', 'position': 'vref_when_odtoff', 'shift': 30, 'mask': 0x3, 'version': 5},

    'lp4_f1_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'ddr_freq0_1', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_lp4_ddr_freq0_1_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'ddr_freq0_1', 'shift': 24, 'mask': 0xff, 'version': 2},
    'lp4_f2_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'ddr_freq2_3', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'lp4_f3_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'ddr_freq2_3', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_lp4_ddr_freq2_3_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'ddr_freq2_3', 'shift': 24, 'mask': 0xff, 'version': 2},
    'lp4_f4_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'ddr_freq4_5', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'lp4_f5_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'ddr_freq4_5', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_lp4_ddr_freq4_5_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'ddr_freq4_5', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp4_dq_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'drv_when_odten', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp4_ca_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'drv_when_odten', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_lp4_clk_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'drv_when_odten', 'shift': 16, 'mask': 0xff, 'version': 2},
    'lp4_dq_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'drv_when_odten', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp4_dq_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'drv_when_odtoff', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp4_ca_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'drv_when_odtoff', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_lp4_clk_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'drv_when_odtoff', 'shift': 16, 'mask': 0xff, 'version': 2},
    'lp4_dq_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'drv_when_odtoff', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp4_odt_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'odt_info', 'shift': 8, 'mask': 0x3ff, 'version': 2},
    'lp4_odt_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'odt_info', 'shift': 0, 'mask': 0xff, 'version': 2},
    'lp4_ca_odt_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'odt_info', 'shift': 18, 'mask': 0xff, 'version': 2},
    'lp4_drv_pu_cal_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'odt_info', 'shift': 26, 'mask': 0x1, 'version': 2},
    'lp4_drv_pu_cal_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'odt_info', 'shift': 27, 'mask': 0x1, 'version': 2},
    'phy_lp4_drv_pull_dn_en_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'odt_info', 'shift': 28, 'mask': 0x1, 'version': 2},
    'phy_lp4_drv_pull_dn_en_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'odt_info', 'shift': 29, 'mask': 0x1, 'version': 2},
    'reserved_lp4_odt_info_bit31': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'odt_info', 'shift': 31, 'mask': 0x1, 'version': 2},
    'phy_lp4_odten_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'dq_odten_freq', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'lp4_dq_odten_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'dq_odten_freq', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'reserved_lp4_dq_odten_freq_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'dq_odten_freq', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp4_dq_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'sr_when_odten', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp4_ca_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'sr_when_odten', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_lp4_clk_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'sr_when_odten', 'shift': 16, 'mask': 0xff, 'version': 2},
    'reserved_lp4_sr_when_odten_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'sr_when_odten', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp4_dq_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'sr_when_odtoff', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp4_ca_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'sr_when_odtoff', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_lp4_clk_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'sr_when_odtoff', 'shift': 16, 'mask': 0xff, 'version': 2},
    'reserved_lp4_sr_when_odtoff_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'sr_when_odtoff', 'shift': 24, 'mask': 0xff, 'version': 2},
    'lp4_ca_odten_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'ca_odten_freq', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'reserved_lp4_ca_odten_freq_bit12_31': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'ca_odten_freq', 'shift': 12, 'mask': 0xfffff, 'version': 2},
    'phy_lp4_cs_drv_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'cs_drv_ca_odt_info', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp4_cs_drv_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'cs_drv_ca_odt_info', 'shift': 8, 'mask': 0xff, 'version': 2},
    'lp4_odte_ck': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'cs_drv_ca_odt_info', 'shift': 16, 'mask': 0x1, 'version': 2},
    'lp4_odte_cs_en': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'cs_drv_ca_odt_info', 'shift': 17, 'mask': 0x1, 'version': 2},
    'lp4_odtd_ca_en': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'cs_drv_ca_odt_info', 'shift': 18, 'mask': 0x1, 'version': 2},
    'reserved_lp4cs_drv_ca_odt_info_bit19_31': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'cs_drv_ca_odt_info', 'shift': 19, 'mask': 0x1fff, 'version': 2},
    'phy_lp4_dq_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'vref_when_odten', 'shift': 0, 'mask': 0x3ff, 'version': 2},
    'lp4_dq_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'vref_when_odten', 'shift': 10, 'mask': 0x3ff, 'version': 2},
    'lp4_ca_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'vref_when_odten', 'shift': 20, 'mask': 0x3ff, 'version': 2},
    'reserved_lp4_vref_when_odten_bit30_31': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'vref_when_odten', 'shift': 30, 'mask': 0x3, 'version': 2},
    'phy_lp4_dq_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'vref_when_odtoff', 'shift': 0, 'mask': 0x3ff, 'version': 2},
    'lp4_dq_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'vref_when_odtoff', 'shift': 10, 'mask': 0x3ff, 'version': 2},
    'lp4_ca_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'vref_when_odtoff', 'shift': 20, 'mask': 0x3ff, 'version': 2},
    'reserved_lp4_vref_when_odtoff_bit30_31': {'value': 0, 'num_base': 'dec', 'index': 'lp4_index', 'position': 'vref_when_odtoff', 'shift': 30, 'mask': 0x3, 'version': 2},

    'ddr2_bytes_map': {'value': 0, 'num_base': 'hex', 'index': 'dq_map_index', 'position': 'byte_map_0', 'shift': 16, 'mask': 0xff, 'version': 2},
    'ddr3_bytes_map': {'value': 0, 'num_base': 'hex', 'index': 'dq_map_index', 'position': 'byte_map_0', 'shift': 24, 'mask': 0xff, 'version': 2},
    'ddr4_bytes_map': {'value': 0, 'num_base': 'hex', 'index': 'dq_map_index', 'position': 'byte_map_0', 'shift': 0, 'mask': 0xff, 'version': 2},
    'reservedbyte_map_0_bit8_15': {'value': 0, 'num_base': 'hex', 'index': 'dq_map_index', 'position': 'byte_map_0', 'shift': 8, 'mask': 0xff, 'version': 2},
    'lp2_bytes_map': {'value': 0, 'num_base': 'hex', 'index': 'dq_map_index', 'position': 'byte_map_1', 'shift': 8, 'mask': 0xff, 'version': 2},
    'lp3_bytes_map': {'value': 0, 'num_base': 'hex', 'index': 'dq_map_index', 'position': 'byte_map_1', 'shift': 16, 'mask': 0xff, 'version': 2},
    'lp4_bytes_map': {'value': 0, 'num_base': 'hex', 'index': 'dq_map_index', 'position': 'byte_map_1', 'shift': 24, 'mask': 0xff, 'version': 2},
    'reserved_byte_map_1_bit0_7': {'value': 0, 'num_base': 'hex', 'index': 'dq_map_index', 'position': 'byte_map_1', 'shift': 0, 'mask': 0xff, 'version': 2},
    'lp3_dq0_7_map': {'value': 0, 'num_base': 'hex', 'index': 'dq_map_index', 'position': 'lp3_dq0_7_map', 'shift': 0, 'mask': 0xffffffff, 'version': 2},
    'lp2_dq0_7_map': {'value': 0, 'num_base': 'hex', 'index': 'dq_map_index', 'position': 'lp2_dq0_7_map', 'shift': 0, 'mask': 0xffffffff, 'version': 2},
    'ddr4_cs0_dq0_dq15_map': {'value': 0, 'num_base': 'hex', 'index': 'dq_map_index', 'position': 'ddr4_dq_map_0', 'shift': 0, 'mask': 0xffffffff, 'version': 2},
    'ddr4_cs0_dq16_dq31_map': {'value': 0, 'num_base': 'hex', 'index': 'dq_map_index', 'position': 'ddr4_dq_map_1', 'shift': 0, 'mask': 0xffffffff, 'version': 2},
    'ddr4_cs1_dq0_dq15_map': {'value': 0, 'num_base': 'hex', 'index': 'dq_map_index', 'position': 'ddr4_dq_map_2', 'shift': 0, 'mask': 0xffffffff, 'version': 2},
    'ddr4_cs1_dq16_dq31_map': {'value': 0, 'num_base': 'hex', 'index': 'dq_map_index', 'position': 'ddr4_dq_map_3', 'shift': 0, 'mask': 0xffffffff, 'version': 2},

    'lp4x_f1_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'ddr_freq0_1', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_lp4x_ddr_freq0_1_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'ddr_freq0_1', 'shift': 24, 'mask': 0xff, 'version': 2},
    'lp4x_f2_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'ddr_freq2_3', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'lp4x_f3_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'ddr_freq2_3', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_lp4x_ddr_freq2_3_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'ddr_freq2_3', 'shift': 24, 'mask': 0xff, 'version': 2},
    'lp4x_f4_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'ddr_freq4_5', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'lp4x_f5_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'ddr_freq4_5', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_lp4x_ddr_freq4_5_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'ddr_freq4_5', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp4x_dq_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'drv_when_odten', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp4x_ca_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'drv_when_odten', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_lp4x_clk_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'drv_when_odten', 'shift': 16, 'mask': 0xff, 'version': 2},
    'lp4x_dq_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'drv_when_odten', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp4x_dq_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'drv_when_odtoff', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp4x_ca_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'drv_when_odtoff', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_lp4x_clk_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'drv_when_odtoff', 'shift': 16, 'mask': 0xff, 'version': 2},
    'lp4x_dq_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'drv_when_odtoff', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp4x_odt_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'odt_info', 'shift': 8, 'mask': 0x3ff, 'version': 2},
    'lp4x_odt_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'odt_info', 'shift': 0, 'mask': 0xff, 'version': 2},
    'lp4x_ca_odt_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'odt_info', 'shift': 18, 'mask': 0xff, 'version': 2},
    'lp4x_drv_pu_cal_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'odt_info', 'shift': 26, 'mask': 0x1, 'version': 2},
    'lp4x_drv_pu_cal_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'odt_info', 'shift': 27, 'mask': 0x1, 'version': 2},
    'phy_lp4x_drv_pull_dn_en_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'odt_info', 'shift': 28, 'mask': 0x1, 'version': 2},
    'phy_lp4x_drv_pull_dn_en_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'odt_info', 'shift': 29, 'mask': 0x1, 'version': 2},
    'reserved_lp4x_odt_info_bit31': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'odt_info', 'shift': 31, 'mask': 0x1, 'version': 2},
    'phy_lp4x_odten_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'dq_odten_freq', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'lp4x_dq_odten_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'dq_odten_freq', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'reserved_lp4x_dq_odten_freq_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'dq_odten_freq', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp4x_dq_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'sr_when_odten', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp4x_ca_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'sr_when_odten', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_lp4x_clk_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'sr_when_odten', 'shift': 16, 'mask': 0xff, 'version': 2},
    'reserved_lp4x_sr_when_odten_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'sr_when_odten', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp4x_dq_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'sr_when_odtoff', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp4x_ca_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'sr_when_odtoff', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_lp4x_clk_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'sr_when_odtoff', 'shift': 16, 'mask': 0xff, 'version': 2},
    'reserved_lp4x_sr_when_odtoff_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'sr_when_odtoff', 'shift': 24, 'mask': 0xff, 'version': 2},
    'lp4x_ca_odten_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'ca_odten_freq', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'reserved_lp4x_ca_odten_freq_bit12_31': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'ca_odten_freq', 'shift': 12, 'mask': 0xfffff, 'version': 2},
    'phy_lp4x_cs_drv_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'cs_drv_ca_odt_info', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp4x_cs_drv_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'cs_drv_ca_odt_info', 'shift': 8, 'mask': 0xff, 'version': 2},
    'lp4x_odte_ck': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'cs_drv_ca_odt_info', 'shift': 16, 'mask': 0x1, 'version': 2},
    'lp4x_odte_cs_en': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'cs_drv_ca_odt_info', 'shift': 17, 'mask': 0x1, 'version': 2},
    'lp4x_odtd_ca_en': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'cs_drv_ca_odt_info', 'shift': 18, 'mask': 0x1, 'version': 2},
    'reserved_lp4xcs_drv_ca_odt_info_bit19_31': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'cs_drv_ca_odt_info', 'shift': 19, 'mask': 0x1fff, 'version': 2},
    'phy_lp4x_dq_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'vref_when_odten', 'shift': 0, 'mask': 0x3ff, 'version': 2},
    'lp4x_dq_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'vref_when_odten', 'shift': 10, 'mask': 0x3ff, 'version': 2},
    'lp4x_ca_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'vref_when_odten', 'shift': 20, 'mask': 0x3ff, 'version': 2},
    'reserved_lp4x_vref_when_odten_bit30_31': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'vref_when_odten', 'shift': 30, 'mask': 0x3, 'version': 2},
    'phy_lp4x_dq_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'vref_when_odtoff', 'shift': 0, 'mask': 0x3ff, 'version': 2},
    'lp4x_dq_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'vref_when_odtoff', 'shift': 10, 'mask': 0x3ff, 'version': 2},
    'lp4x_ca_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'vref_when_odtoff', 'shift': 20, 'mask': 0x3ff, 'version': 2},
    'reserved_lp4x_vref_when_odtoff_bit30_31': {'value': 0, 'num_base': 'dec', 'index': 'lp4x_index', 'position': 'vref_when_odtoff', 'shift': 30, 'mask': 0x3, 'version': 2},

    'lp5_f1_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'ddr_freq0_1', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_lp5_ddr_freq0_1_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'ddr_freq0_1', 'shift': 24, 'mask': 0xff, 'version': 2},
    'lp5_f2_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'ddr_freq2_3', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'lp5_f3_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'ddr_freq2_3', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_lp5_ddr_freq2_3_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'ddr_freq2_3', 'shift': 24, 'mask': 0xff, 'version': 2},
    'lp5_f4_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'ddr_freq4_5', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'lp5_f5_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'ddr_freq4_5', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'reserved_lp5_ddr_freq4_5_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'ddr_freq4_5', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp5_dq_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'drv_when_odten', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp5_ca_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'drv_when_odten', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_lp5_clk_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'drv_when_odten', 'shift': 16, 'mask': 0xff, 'version': 2},
    'lp5_dq_drv_when_odten_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'drv_when_odten', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp5_dq_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'drv_when_odtoff', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp5_ca_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'drv_when_odtoff', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_lp5_clk_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'drv_when_odtoff', 'shift': 16, 'mask': 0xff, 'version': 2},
    'lp5_dq_drv_when_odtoff_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'drv_when_odtoff', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp5_odt_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'odt_info', 'shift': 8, 'mask': 0x3ff, 'version': 2},
    'lp5_odt_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'odt_info', 'shift': 0, 'mask': 0xff, 'version': 2},
    'lp5_ca_odt_ohm': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'odt_info', 'shift': 18, 'mask': 0xff, 'version': 2},
    'lp5_drv_pu_cal_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'odt_info', 'shift': 26, 'mask': 0x1, 'version': 2},
    'lp5_drv_pu_cal_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'odt_info', 'shift': 27, 'mask': 0x1, 'version': 2},
    'phy_lp5_drv_pull_dn_en_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'odt_info', 'shift': 28, 'mask': 0x1, 'version': 2},
    'phy_lp5_drv_pull_dn_en_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'odt_info', 'shift': 29, 'mask': 0x1, 'version': 2},
    'reserved_lp5_odt_info_bit31': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'odt_info', 'shift': 31, 'mask': 0x1, 'version': 2},
    'phy_lp5_odten_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'dq_odten_freq', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'lp5_dq_odten_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'dq_odten_freq', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'reserved_lp5_dq_odten_freq_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'dq_odten_freq', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp5_dq_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'sr_when_odten', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp5_ca_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'sr_when_odten', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_lp5_clk_sr_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'sr_when_odten', 'shift': 16, 'mask': 0xff, 'version': 2},
    'reserved_lp5_sr_when_odten_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'sr_when_odten', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp5_dq_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'sr_when_odtoff', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp5_ca_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'sr_when_odtoff', 'shift': 8, 'mask': 0xff, 'version': 2},
    'phy_lp5_clk_sr_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'sr_when_odtoff', 'shift': 16, 'mask': 0xff, 'version': 2},
    'reserved_lp5_sr_when_odtoff_bit24_31': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'sr_when_odtoff', 'shift': 24, 'mask': 0xff, 'version': 2},
    'lp5_ca_odten_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'ca_odten_freq', 'shift': 0, 'mask': 0xfff, 'version': 2},
    'lp5_wck_odt_en_freq': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'ca_odten_freq', 'shift': 12, 'mask': 0xfff, 'version': 2},
    'lp5_wck_odt': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'ca_odten_freq', 'shift': 24, 'mask': 0xff, 'version': 2},
    'phy_lp5_cs_drv_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'cs_drv_ca_odt_info', 'shift': 0, 'mask': 0xff, 'version': 2},
    'phy_lp5_cs_drv_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'cs_drv_ca_odt_info', 'shift': 8, 'mask': 0xff, 'version': 2},
    'lp5_odte_ck': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'cs_drv_ca_odt_info', 'shift': 16, 'mask': 0x1, 'version': 2},
    'lp5_odte_cs_en': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'cs_drv_ca_odt_info', 'shift': 17, 'mask': 0x1, 'version': 2},
    'lp5_odtd_ca_en': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'cs_drv_ca_odt_info', 'shift': 18, 'mask': 0x1, 'version': 2},
    'lp5_nt_odt': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'cs_drv_ca_odt_info', 'shift': 24, 'mask': 0xff, 'version': 2},
    'reserved_lp5_cs_drv_ca_odt_info_bit19_23': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'cs_drv_ca_odt_info', 'shift': 19, 'mask': 0x1f, 'version': 2},
    'phy_lp5_dq_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'vref_when_odten', 'shift': 0, 'mask': 0x3ff, 'version': 2},
    'lp5_dq_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'vref_when_odten', 'shift': 10, 'mask': 0x3ff, 'version': 2},
    'lp5_ca_vref_when_odten': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'vref_when_odten', 'shift': 20, 'mask': 0x3ff, 'version': 2},
    'reserved_lp5_vref_when_odten_bit30_31': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'vref_when_odten', 'shift': 30, 'mask': 0x3, 'version': 2},
    'phy_lp5_dq_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'vref_when_odtoff', 'shift': 0, 'mask': 0x3ff, 'version': 2},
    'lp5_dq_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'vref_when_odtoff', 'shift': 10, 'mask': 0x3ff, 'version': 2},
    'lp5_ca_vref_when_odtoff': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'vref_when_odtoff', 'shift': 20, 'mask': 0x3ff, 'version': 2},
    'reserved_lp5_vref_when_odtoff_bit30_31': {'value': 0, 'num_base': 'dec', 'index': 'lp5_index', 'position': 'vref_when_odtoff', 'shift': 30, 'mask': 0x3, 'version': 2},

    'lp4_4x_ch_mask0': {'value': 0, 'num_base': 'hex', 'index': 'lp4_4x_hash_index', 'position': 'ch_mask_0', 'shift': 0, 'mask': 0xffffffff, 'version': 3},
    'lp4_4x_ch_mask1': {'value': 0, 'num_base': 'hex', 'index': 'lp4_4x_hash_index', 'position': 'ch_mask_1', 'shift': 0, 'mask': 0xffffffff, 'version': 3},
    'lp4_4x_bank_mask0': {'value': 0, 'num_base': 'hex', 'index': 'lp4_4x_hash_index', 'position': 'bank_mask_0', 'shift': 0, 'mask': 0xffffffff, 'version': 3},
    'lp4_4x_bank_mask1': {'value': 0, 'num_base': 'hex', 'index': 'lp4_4x_hash_index', 'position': 'bank_mask_1', 'shift': 0, 'mask': 0xffffffff, 'version': 3},
    'lp4_4x_bank_mask2': {'value': 0, 'num_base': 'hex', 'index': 'lp4_4x_hash_index', 'position': 'bank_mask_2', 'shift': 0, 'mask': 0xffffffff, 'version': 3},
    'lp4_4x_bank_mask3': {'value': 0, 'num_base': 'hex', 'index': 'lp4_4x_hash_index', 'position': 'bank_mask_3', 'shift': 0, 'mask': 0xffffffff, 'version': 3},
    'lp4_4x_rank_mask0': {'value': 0, 'num_base': 'hex', 'index': 'lp4_4x_hash_index', 'position': 'rank_mask0', 'shift': 0, 'mask': 0xffffffff, 'version': 3},
    'lp4_4x_rank_mask1': {'value': 0, 'num_base': 'hex', 'index': 'lp4_4x_hash_index', 'position': 'rank_mask1', 'shift': 0, 'mask': 0xffffffff, 'version': 3},

    'lp5_ch_mask0': {'value': 0, 'num_base': 'hex', 'index': 'lp5_hash_index', 'position': 'ch_mask_0', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'lp5_ch_mask1': {'value': 0, 'num_base': 'hex', 'index': 'lp5_hash_index', 'position': 'ch_mask_1', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'lp5_bank_mask0': {'value': 0, 'num_base': 'hex', 'index': 'lp5_hash_index', 'position': 'bank_mask_0', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'lp5_bank_mask1': {'value': 0, 'num_base': 'hex', 'index': 'lp5_hash_index', 'position': 'bank_mask_1', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'lp5_bank_mask2': {'value': 0, 'num_base': 'hex', 'index': 'lp5_hash_index', 'position': 'bank_mask_2', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'lp5_bank_mask3': {'value': 0, 'num_base': 'hex', 'index': 'lp5_hash_index', 'position': 'bank_mask_3', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'lp5_rank_mask0': {'value': 0, 'num_base': 'hex', 'index': 'lp5_hash_index', 'position': 'rank_mask0', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'lp5_rank_mask1': {'value': 0, 'num_base': 'hex', 'index': 'lp5_hash_index', 'position': 'rank_mask1', 'shift': 0, 'mask': 0xffffffff, 'version': 4},

    'ddr4_ch_mask0': {'value': 0, 'num_base': 'hex', 'index': 'ddr4_hash_index', 'position': 'ch_mask_0', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr4_ch_mask1': {'value': 0, 'num_base': 'hex', 'index': 'ddr4_hash_index', 'position': 'ch_mask_1', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr4_bank_mask0': {'value': 0, 'num_base': 'hex', 'index': 'ddr4_hash_index', 'position': 'bank_mask_0', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr4_bank_mask1': {'value': 0, 'num_base': 'hex', 'index': 'ddr4_hash_index', 'position': 'bank_mask_1', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr4_bank_mask2': {'value': 0, 'num_base': 'hex', 'index': 'ddr4_hash_index', 'position': 'bank_mask_2', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr4_bank_mask3': {'value': 0, 'num_base': 'hex', 'index': 'ddr4_hash_index', 'position': 'bank_mask_3', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr4_rank_mask0': {'value': 0, 'num_base': 'hex', 'index': 'ddr4_hash_index', 'position': 'rank_mask0', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr4_rank_mask1': {'value': 0, 'num_base': 'hex', 'index': 'ddr4_hash_index', 'position': 'rank_mask1', 'shift': 0, 'mask': 0xffffffff, 'version': 4},

    'lp3_ch_mask0': {'value': 0, 'num_base': 'hex', 'index': 'lp3_hash_index', 'position': 'ch_mask_0', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'lp3_ch_mask1': {'value': 0, 'num_base': 'hex', 'index': 'lp3_hash_index', 'position': 'ch_mask_1', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'lp3_bank_mask0': {'value': 0, 'num_base': 'hex', 'index': 'lp3_hash_index', 'position': 'bank_mask_0', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'lp3_bank_mask1': {'value': 0, 'num_base': 'hex', 'index': 'lp3_hash_index', 'position': 'bank_mask_1', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'lp3_bank_mask2': {'value': 0, 'num_base': 'hex', 'index': 'lp3_hash_index', 'position': 'bank_mask_2', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'lp3_bank_mask3': {'value': 0, 'num_base': 'hex', 'index': 'lp3_hash_index', 'position': 'bank_mask_3', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'lp3_rank_mask0': {'value': 0, 'num_base': 'hex', 'index': 'lp3_hash_index', 'position': 'rank_mask0', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'lp3_rank_mask1': {'value': 0, 'num_base': 'hex', 'index': 'lp3_hash_index', 'position': 'rank_mask1', 'shift': 0, 'mask': 0xffffffff, 'version': 4},

    'ddr3_ch_mask0': {'value': 0, 'num_base': 'hex', 'index': 'ddr3_hash_index', 'position': 'ch_mask_0', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr3_ch_mask1': {'value': 0, 'num_base': 'hex', 'index': 'ddr3_hash_index', 'position': 'ch_mask_1', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr3_bank_mask0': {'value': 0, 'num_base': 'hex', 'index': 'ddr3_hash_index', 'position': 'bank_mask_0', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr3_bank_mask1': {'value': 0, 'num_base': 'hex', 'index': 'ddr3_hash_index', 'position': 'bank_mask_1', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr3_bank_mask2': {'value': 0, 'num_base': 'hex', 'index': 'ddr3_hash_index', 'position': 'bank_mask_2', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr3_bank_mask3': {'value': 0, 'num_base': 'hex', 'index': 'ddr3_hash_index', 'position': 'bank_mask_3', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr3_rank_mask0': {'value': 0, 'num_base': 'hex', 'index': 'ddr3_hash_index', 'position': 'rank_mask0', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr3_rank_mask1': {'value': 0, 'num_base': 'hex', 'index': 'ddr3_hash_index', 'position': 'rank_mask1', 'shift': 0, 'mask': 0xffffffff, 'version': 4},

    'lp2_ch_mask0': {'value': 0, 'num_base': 'hex', 'index': 'lp2_hash_index', 'position': 'ch_mask_0', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'lp2_ch_mask1': {'value': 0, 'num_base': 'hex', 'index': 'lp2_hash_index', 'position': 'ch_mask_1', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'lp2_bank_mask0': {'value': 0, 'num_base': 'hex', 'index': 'lp2_hash_index', 'position': 'bank_mask_0', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'lp2_bank_mask1': {'value': 0, 'num_base': 'hex', 'index': 'lp2_hash_index', 'position': 'bank_mask_1', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'lp2_bank_mask2': {'value': 0, 'num_base': 'hex', 'index': 'lp2_hash_index', 'position': 'bank_mask_2', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'lp2_bank_mask3': {'value': 0, 'num_base': 'hex', 'index': 'lp2_hash_index', 'position': 'bank_mask_3', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'lp2_rank_mask0': {'value': 0, 'num_base': 'hex', 'index': 'lp2_hash_index', 'position': 'rank_mask0', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'lp2_rank_mask1': {'value': 0, 'num_base': 'hex', 'index': 'lp2_hash_index', 'position': 'rank_mask1', 'shift': 0, 'mask': 0xffffffff, 'version': 4},

    'ddr2_ch_mask0': {'value': 0, 'num_base': 'hex', 'index': 'ddr2_hash_index', 'position': 'ch_mask_0', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr2_ch_mask1': {'value': 0, 'num_base': 'hex', 'index': 'ddr2_hash_index', 'position': 'ch_mask_1', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr2_bank_mask0': {'value': 0, 'num_base': 'hex', 'index': 'ddr2_hash_index', 'position': 'bank_mask_0', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr2_bank_mask1': {'value': 0, 'num_base': 'hex', 'index': 'ddr2_hash_index', 'position': 'bank_mask_1', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr2_bank_mask2': {'value': 0, 'num_base': 'hex', 'index': 'ddr2_hash_index', 'position': 'bank_mask_2', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr2_bank_mask3': {'value': 0, 'num_base': 'hex', 'index': 'ddr2_hash_index', 'position': 'bank_mask_3', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr2_rank_mask0': {'value': 0, 'num_base': 'hex', 'index': 'ddr2_hash_index', 'position': 'rank_mask0', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr2_rank_mask1': {'value': 0, 'num_base': 'hex', 'index': 'ddr2_hash_index', 'position': 'rank_mask1', 'shift': 0, 'mask': 0xffffffff, 'version': 4},

    'ddr5_ch_mask0': {'value': 0, 'num_base': 'hex', 'index': 'ddr5_hash_index', 'position': 'ch_mask_0', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr5_ch_mask1': {'value': 0, 'num_base': 'hex', 'index': 'ddr5_hash_index', 'position': 'ch_mask_1', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr5_bank_mask0': {'value': 0, 'num_base': 'hex', 'index': 'ddr5_hash_index', 'position': 'bank_mask_0', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr5_bank_mask1': {'value': 0, 'num_base': 'hex', 'index': 'ddr5_hash_index', 'position': 'bank_mask_1', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr5_bank_mask2': {'value': 0, 'num_base': 'hex', 'index': 'ddr5_hash_index', 'position': 'bank_mask_2', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr5_bank_mask3': {'value': 0, 'num_base': 'hex', 'index': 'ddr5_hash_index', 'position': 'bank_mask_3', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr5_rank_mask0': {'value': 0, 'num_base': 'hex', 'index': 'ddr5_hash_index', 'position': 'rank_mask0', 'shift': 0, 'mask': 0xffffffff, 'version': 4},
    'ddr5_rank_mask1': {'value': 0, 'num_base': 'hex', 'index': 'ddr5_hash_index', 'position': 'rank_mask1', 'shift': 0, 'mask': 0xffffffff, 'version': 4},

    'reserved_skew_ddr3_skew_freq_bit12_31': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_skew_freq', 'shift': 12, 'mask': 0xfffff, 'version': 4},
    'ddr3_skew_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'skew_index', 'position': 'ddr3_skew_freq', 'shift': 0, 'mask': 0xfff, 'version': 4},
    'ddr3_ca0_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_2', 'shift': 8, 'mask': 0xff, 'version': 4},
    'ddr3_ca1_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_0', 'shift': 0, 'mask': 0xff, 'version': 4},
    'ddr3_ca2_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_1', 'shift': 24, 'mask': 0xff, 'version': 4},
    'ddr3_ca3_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_1', 'shift': 8, 'mask': 0xff, 'version': 4},
    'ddr3_ca4_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_1', 'shift': 16, 'mask': 0xff, 'version': 4},
    'ddr3_ca5_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_2', 'shift': 24, 'mask': 0xff, 'version': 4},
    'ddr3_ca6_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_1', 'shift': 0, 'mask': 0xff, 'version': 4},
    'ddr3_ca7_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_2', 'shift': 0, 'mask': 0xff, 'version': 4},
    'ddr3_ca8_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_3', 'shift': 16, 'mask': 0xff, 'version': 4},
    'ddr3_ca9_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_0', 'shift': 24, 'mask': 0xff, 'version': 4},
    'ddr3_ca10_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_3', 'shift': 24, 'mask': 0xff, 'version': 4},
    'ddr3_ca11_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_2', 'shift': 16, 'mask': 0xff, 'version': 4},
    'ddr3_ca12_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_4', 'shift': 0, 'mask': 0xff, 'version': 4},
    'ddr3_ca13_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_0', 'shift': 8, 'mask': 0xff, 'version': 4},
    'ddr3_ca14_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_0', 'shift': 16, 'mask': 0xff, 'version': 4},
    'ddr3_ca15_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_5', 'shift': 16, 'mask': 0xff, 'version': 4},
    'ddr3_ras_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_5', 'shift': 8, 'mask': 0xff, 'version': 4},
    'ddr3_cas_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_7', 'shift': 24, 'mask': 0xff, 'version': 4},
    'ddr3_ba0_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_5', 'shift': 24, 'mask': 0xff, 'version': 4},
    'ddr3_ba1_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_3', 'shift': 0, 'mask': 0xff, 'version': 4},
    'ddr3_ba2_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_4', 'shift': 8, 'mask': 0xff, 'version': 4},
    'ddr3_we_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_6', 'shift': 8, 'mask': 0xff, 'version': 4},
    'ddr3_cke0_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_4', 'shift': 24, 'mask': 0xff, 'version': 4},
    'ddr3_cke1_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_5', 'shift': 0, 'mask': 0xff, 'version': 4},
    'ddr3_ckn_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_6', 'shift': 24, 'mask': 0xff, 'version': 4},
    'ddr3_ckp_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_6', 'shift': 16, 'mask': 0xff, 'version': 4},
    'ddr3_odt0_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_3', 'shift': 8, 'mask': 0xff, 'version': 4},
    'ddr3_odt1_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_6', 'shift': 0, 'mask': 0xff, 'version': 4},
    'ddr3_cs0_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_7', 'shift': 0, 'mask': 0xff, 'version': 4},
    'ddr3_cs1_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_7', 'shift': 16, 'mask': 0xff, 'version': 4},
    'ddr3_resetn_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr3_ca_skew_7', 'shift': 8, 'mask': 0xff, 'version': 4},

    'reserved_skew_ddr4_skew_freq_bit12_31': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_skew_freq', 'shift': 12, 'mask': 0xfffff, 'version': 4},
    'ddr4_skew_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'skew_index', 'position': 'ddr4_skew_freq', 'shift': 0, 'mask': 0xfff, 'version': 4},
    'ddr4_ca0_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_0', 'shift': 24, 'mask': 0xff, 'version': 4},
    'ddr4_ca1_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_0', 'shift': 16, 'mask': 0xff, 'version': 4},
    'ddr4_ca2_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_0', 'shift': 8, 'mask': 0xff, 'version': 4},
    'ddr4_ca3_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_0', 'shift': 0, 'mask': 0xff, 'version': 4},
    'ddr4_ca4_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_1', 'shift': 24, 'mask': 0xff, 'version': 4},
    'ddr4_ca5_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_1', 'shift': 16, 'mask': 0xff, 'version': 4},
    'ddr4_ca6_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_1', 'shift': 8, 'mask': 0xff, 'version': 4},
    'ddr4_ca7_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_1', 'shift': 0, 'mask': 0xff, 'version': 4},
    'ddr4_ca8_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_2', 'shift': 24, 'mask': 0xff, 'version': 4},
    'ddr4_ca9_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_2', 'shift': 16, 'mask': 0xff, 'version': 4},
    'ddr4_ca10_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_2', 'shift': 8, 'mask': 0xff, 'version': 4},
    'ddr4_ca11_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_2', 'shift': 0, 'mask': 0xff, 'version': 4},
    'ddr4_ca12_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_3', 'shift': 24, 'mask': 0xff, 'version': 4},
    'ddr4_ca13_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_3', 'shift': 16, 'mask': 0xff, 'version': 4},
    'ddr4_ca14_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_3', 'shift': 8, 'mask': 0xff, 'version': 4},
    'ddr4_ca15_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_3', 'shift': 0, 'mask': 0xff, 'version': 4},
    'ddr4_ca16_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_4', 'shift': 24, 'mask': 0xff, 'version': 4},
    'ddr4_ca17_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_4', 'shift': 16, 'mask': 0xff, 'version': 4},
    'ddr4_ba0_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_4', 'shift': 8, 'mask': 0xff, 'version': 4},
    'ddr4_ba1_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_4', 'shift': 0, 'mask': 0xff, 'version': 4},
    'ddr4_bg0_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_5', 'shift': 24, 'mask': 0xff, 'version': 4},
    'ddr4_bg1_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_5', 'shift': 16, 'mask': 0xff, 'version': 4},
    'ddr4_cke0_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_5', 'shift': 8, 'mask': 0xff, 'version': 4},
    'ddr4_cke1_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_5', 'shift': 0, 'mask': 0xff, 'version': 4},
    'ddr4_ckn_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_6', 'shift': 24, 'mask': 0xff, 'version': 4},
    'ddr4_ckp_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_6', 'shift': 16, 'mask': 0xff, 'version': 4},
    'ddr4_odt0_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_6', 'shift': 8, 'mask': 0xff, 'version': 4},
    'ddr4_odt1_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_6', 'shift': 0, 'mask': 0xff, 'version': 4},
    'ddr4_cs0_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_7', 'shift': 24, 'mask': 0xff, 'version': 4},
    'ddr4_cs1_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_7', 'shift': 16, 'mask': 0xff, 'version': 4},
    'ddr4_resetn_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_7', 'shift': 8, 'mask': 0xff, 'version': 4},
    'ddr4_actn_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'ddr4_ca_skew_7', 'shift': 0, 'mask': 0xff, 'version': 4},

    'reserved_skew_lp3_skew_freq_bit12_31': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'lp3_skew_freq', 'shift': 12, 'mask': 0xfffff, 'version': 4},
    'lp3_skew_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'skew_index', 'position': 'lp3_skew_freq', 'shift': 0, 'mask': 0xfff, 'version': 4},
    'lp3_ca0_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'lp3_ca_skew_3', 'shift': 0, 'mask': 0xff, 'version': 4},
    'lp3_ca1_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'lp3_ca_skew_4', 'shift': 0, 'mask': 0xff, 'version': 4},
    'lp3_ca2_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'lp3_ca_skew_2', 'shift': 16, 'mask': 0xff, 'version': 4},
    'lp3_ca3_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'lp3_ca_skew_3', 'shift': 16, 'mask': 0xff, 'version': 4},
    'lp3_ca4_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'lp3_ca_skew_3', 'shift': 24, 'mask': 0xff, 'version': 4},
    'lp3_ca5_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'lp3_ca_skew_1', 'shift': 24, 'mask': 0xff, 'version': 4},
    'lp3_ca6_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'lp3_ca_skew_2', 'shift': 24, 'mask': 0xff, 'version': 4},
    'lp3_ca7_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'lp3_ca_skew_2', 'shift': 0, 'mask': 0xff, 'version': 4},
    'lp3_ca8_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'lp3_ca_skew_5', 'shift': 24, 'mask': 0xff, 'version': 4},
    'lp3_ca9_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'lp3_ca_skew_7', 'shift': 0, 'mask': 0xff, 'version': 4},
    'lp3_cke0_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'lp3_ca_skew_4', 'shift': 8, 'mask': 0xff, 'version': 4},
    'lp3_cke1_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'lp3_ca_skew_5', 'shift': 0, 'mask': 0xff, 'version': 4},
    'lp3_ckn_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'lp3_ca_skew_6', 'shift': 24, 'mask': 0xff, 'version': 4},
    'lp3_ckp_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'lp3_ca_skew_6', 'shift': 16, 'mask': 0xff, 'version': 4},
    'lp3_odt0_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'lp3_ca_skew_6', 'shift': 8, 'mask': 0xff, 'version': 4},
    'lp3_odt1_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'lp3_ca_skew_6', 'shift': 0, 'mask': 0xff, 'version': 4},
    'lp3_odt2_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'lp3_ca_skew_0', 'shift': 24, 'mask': 0xff, 'version': 4},
    'lp3_odt3_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'lp3_ca_skew_0', 'shift': 8, 'mask': 0xff, 'version': 4},
    'lp3_cs0_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'lp3_ca_skew_7', 'shift': 16, 'mask': 0xff, 'version': 4},
    'lp3_cs1_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'lp3_ca_skew_7', 'shift': 24, 'mask': 0xff, 'version': 4},
    'lp3_cs2_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'lp3_ca_skew_1', 'shift': 8, 'mask': 0xff, 'version': 4},
    'lp3_cs3_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'lp3_ca_skew_3', 'shift': 8, 'mask': 0xff, 'version': 4},

    'reserved_skew_lp4_skew_freq_bit12_31': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_skew_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_ca0_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_ca1_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_ca2_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_ca3_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_ca4_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_ca5_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_odt0_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_odt1_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_cke0_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_cke1_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_ckn_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_ckp_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_cs0_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_cs1_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_ca0_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_ca1_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_ca2_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_ca3_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_ca4_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_ca5_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_odt0_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_odt1_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_cke0_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_cke1_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_ckn_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_ckp_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_cs0_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_cs1_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp4_resetn_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},

    'reserved_skew_lp5_skew_freq_bit12_31': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_skew_freq_mhz': {'value': 0, 'num_base': 'dec', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_ca0_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_ca1_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_ca2_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_ca3_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_ca4_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_ca5_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_ca6_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_ckn_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_ckp_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_cs0_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_cs1_a_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_ca0_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_ca1_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_ca2_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_ca3_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_ca4_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_ca5_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_ca6_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_ckn_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_ckp_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_cs0_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_cs1_b_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
    'lp5_resetn_skew': {'value': 0, 'num_base': 'hex', 'index': 'skew_index', 'position': 'null', 'shift': 0, 'mask': 0, 'version': 4},
}


def bin_data_2_info(info_from_bin, read_out, ddrbin_index, version, info_from_txt):
    info_from_bin['start tag']['value'] = 0x12345678

    if version < 2:
        for key, value in info_from_bin.items():
            if value['version'] <= version:
                for i in range(len(read_out)):
                    # read_out is sdram_head_info_v0 = [[offset, value], ...]
                    # info_from_bin v0_info = [offset, shift, mask]
                    if value['v0_info'][0] == read_out[i][0]:
                        temp_value = (read_out[i][1] >> value['v0_info'][1]) & value['v0_info'][2]
                        info_from_bin[key]['value'] = temp_value
                        #print(f"D: {key} = {value} {hex(value['v0_info'][0])}={read_out[i][1]}")
    elif version <= version_max:
        for index_name in ddrbin_index:
            head_info_name = index_name[:-6]+'_info'
            if ddrbin_index[index_name]['offset'] != 0 and 'skew' not in index_name:
                for key, value in info_from_bin.items():
                    if value['index'] == index_name and value['version'] <= version:
                        temp_value = read_out[head_info_name][value['position']]
                        temp_value = (temp_value >> value['shift']) & value['mask']
                        info_from_bin[key]['value'] = temp_value
                        #print(f"D: {key} = {value} {value['position']}={temp_value}")
            elif ddrbin_index[index_name]['offset'] != 0 and 'skew' in index_name:
                if chip_info == 'rk3528':
                    for key, value in info_from_bin.items():
                        if value['index'] == index_name and value['version'] <= version:
                            position_1 = value['position'][ : value['position'].find('_')]
                            position_2 = value['position'][value['position'].find('_') + 1 : ]
                            # read_out is sdram_head_info_v2 or sdram_head_info_v5
                            if position_1 in list(read_out[head_info_name].keys()):
                                temp_value = read_out[head_info_name][position_1][position_2]
                                temp_value = (temp_value >> value['shift']) & value['mask']
                                info_from_bin[key]['value'] = temp_value
                                #print(f"D: {key} = {value} {value['position']}={temp_value}")

    return 0


def modefy_2_bin_data(info_from_txt, write_in, ddrbin_index, version):
    global rk3528_skew_info

    if version < 2:
        for key, value in info_from_txt.items():
            if value['version'] <= version:
                for i in range(len(write_in)):
                    if value['v0_info'][0] == write_in[i][0]:
                        write_in[i][1] |= (value['value'] << value['v0_info'][1])
    elif version <= version_max:
        for index_name in ddrbin_index:
            head_info_name = index_name[:-6]+'_info'
            if ddrbin_index[index_name]['offset'] != 0 and 'skew' not in index_name:
                position_name = 'null'
                for key, value in info_from_txt.items():
                    if value['index'] == index_name and value['version'] <= version:
                        if position_name != value['position']:
                            position_name = value['position']
                            position_value = 0
                        position_value |= (value['value'] << value['shift'])
                        write_in[head_info_name][value['position']] = position_value
                        #print(f"D: {key} = {value}, {value['position']}={position_value}")
            elif ddrbin_index[index_name]['offset'] != 0 and 'skew' in index_name:
                if chip_info == 'rk3528':
                    write_in.update({'skew_info' : rk3528_skew_info})
                    if rk3528_skew_info['skew_sub_version'] == 0x1:
                        for key, value in info_from_txt.items():
                            if value['index'] == index_name and value['version'] <= version:
                                position_1 = value['position'][ : value['position'].find('_')]
                                position_2 = value['position'][value['position'].find('_') + 1 : ]
                                if position_1 in list(write_in[head_info_name].keys()):
                                    temp_value =  write_in[head_info_name][position_1][position_2]
                                    temp_value &= ~(value['mask'] << value['shift'])
                                    temp_value |= value['value'] << value['shift']
                                    write_in[head_info_name][position_1][position_2] = temp_value
                                    #print(f"D: {key} = {value}, {temp_value}")

    #print(f"D: write_in = {write_in}")
    return 0


def write_in_bin_data_v2(filebin, bin_skew_offset, write_in, ddrbin_index, info_from_txt, version):
    for index_name in ddrbin_index:
        head_info_name = index_name[:-6]+'_info'
        if ddrbin_index[index_name]['offset'] != 0 and 'skew' not in index_name:
            filebin.seek(bin_skew_offset + (ddrbin_index[index_name]['offset'] - 1) * 4)
            index_size = ddrbin_index[index_name]['size']
            for key in write_in[head_info_name]:
                if index_size > 0:
                    try:
                        filebin.write(write_in[head_info_name][key].to_bytes(4,byteorder='little'))
                        #print(f"D: {head_info_name} {key} = {write_in[head_info_name][key]}")
                        index_size -= 1
                    except:
                        print("write bin {} to file fail".format(head_info_name))
                        return -1
        elif ddrbin_index[index_name]['offset'] != 0 and 'skew' in index_name:
            if chip_info == 'rk3528' and write_in[head_info_name]["skew_sub_version"] == 1:
                filebin.seek(bin_skew_offset + (ddrbin_index[index_name]['offset'] - 1) * 4)
                index_size = ddrbin_index[index_name]['size']
                for key in write_in[head_info_name]:
                    if key == 'skew_sub_version':
                        temp_value = write_in[head_info_name]["skew_sub_version"]
                        filebin.write(temp_value.to_bytes(4,byteorder='little'))
                        continue
                    for key_1 in write_in[head_info_name][key]:
                        if index_size > 0:
                            try:
                                temp_value = write_in[head_info_name][key][key_1]
                                #print(f"D: {head_info_name} {key}.{key_1} = {temp_value}")
                                filebin.write(temp_value.to_bytes(4,byteorder='little'))
                                index_size -= 1
                            except:
                                print("write bin {} to file fail".format(head_info_name))
                                return -1

    return 0


#info from bin + info from txt generate to loader parameters
def txt_data_2_bin_data(info_from_txt, info_from_bin, ddrbin_index, write_in, version):
    print("\nnew bin config:")

    for key, value in info_from_txt.items():
        if key == 'start tag':
            continue
        if (info_from_txt[key]['value'] == 0) and (key not in update_key_list):
            info_from_txt[key]['value'] = info_from_bin[key]['value']
        else:
            if info_from_txt[key]['num_base'] == 'hex':
                print("{}: {}".format(key, hex(info_from_txt[key]['value'])))
            else:
                print("{}: {}".format(key, info_from_txt[key]['value']))
    #print(info_from_txt)

    modefy_2_bin_data(info_from_txt, write_in, ddrbin_index, version)

    return 0


def bin_data_readout(filebin, ddrbin_index, read_out, bin_skew_offset, version, info_from_txt):
    global rk3528_skew_info

    if version < 2:
        for i in range(len(read_out)):
            try:
                read_out[i][1] = int.from_bytes(filebin.read(4), byteorder='little')
                #print(f"D: read_out {hex(read_out[i][0])} = {read_out[i][1]}")
            except:
                print("read bin file fail")
                return -1
    elif version <= version_max:
        for index_name in ddrbin_index:
            head_info_name = index_name[:-6]+'_info'
            if ddrbin_index[index_name]['offset'] != 0 and 'skew' not in index_name:
                filebin.seek(bin_skew_offset + (ddrbin_index[index_name]['offset'] - 1) * 4)
                index_size = ddrbin_index[index_name]['size']
                for key in read_out[head_info_name]:
                    if index_size > 0:
                        try:
                            temp_value = int.from_bytes(filebin.read(4), byteorder='little')
                            read_out[head_info_name][key] = temp_value
                            #print(f"D: {head_info_name} {key} = {read_out[head_info_name][key]}")
                            index_size -= 1
                        except:
                            print("read {} from bin file fail".format(head_info_name))
                            return -1
            elif ddrbin_index[index_name]['offset'] != 0 and 'skew' in index_name:
                try:
                    filebin.seek(bin_skew_offset + (ddrbin_index[index_name]['offset'] - 1) * 4)
                    skew_sub_ver = int.from_bytes(filebin.read(4), byteorder='little') & 0xff
                except:
                    print("read skew_sub_ver from bin file fail")
                    return -1
                if chip_info == 'rk3528' and skew_sub_ver == 0x1:
                    for i in rk3528_skew_info:
                        if i == 'skew_sub_version':
                            rk3528_skew_info[i] = skew_sub_ver
                            continue
                        for j in rk3528_skew_info[i]:
                            try:
                                temp_value = int.from_bytes(filebin.read(4), byteorder='little')
                                rk3528_skew_info[i][j] = temp_value
                                #print(f"D: {i}.{j}={rk3528_skew_info[i][j]}")
                            except:
                                print("read {} from bin file fail".format(head_info_name))
                                return -1

                read_out.update({'skew_info' : rk3528_skew_info})

    return 0


def gen_info_from_bin(filegen_path, info_from_bin, verinfo_full, version):
    with open(filegen_path, 'w+', encoding='utf-8') as file:
        file.write('/* ' + verinfo_full + ' */\n')

    with open(filegen_path, 'a', encoding='utf-8') as file:
        for key, value in info_from_bin.items():
            if "reserved" in key:
                continue

            if value['num_base'] == 'hex':
                value_str = str(hex(value['value']))
            else:
                value_str = str(value['value'])

            write_buff = key + '=' + value_str
            #print(f"D: {write_buff}")
            file.write(write_buff + '\n')

    with open(filegen_path, 'a', encoding='utf-8') as file:
        file.write('end' + '\n')

    return 0


def print_help():
    print(
        "For more details, please refer to the ddrbin_tool_user_guide.txt\n"\
        "This tools support two functions\n"\
        "for example:\n"\
        "function 1: modify ddr.bin file from ddrbin_param.txt.\n"\
        "	1) modify 'ddrbin_param.txt', set ddr frequency, uart info etc what you want.\n"\
        "	If want to keep items default, please keep these items blank.\n"\
        "	The date & time in the version information will be updated by default.\n"\
        "	like: ./ddrbin_tool px30 ddrbin_param.txt px30_ddr_333MHz_v1.13.bin\n"\
        "\n"\
        "	OPTION: --verinfo_editable=TEXT		The TEXT(max 17 chars) will replace\n"\
        "						the date & time in the version information.\n"\
        "	like: ./ddrbin_tool px30 ddrbin_param.txt px30_ddr_333MHz_v1.13.bin [OPTION]\n"\
        "\n"\
        "function 2: get ddr.bin file config to gen_param.txt file\n"\
        "	If want to get ddrbin file config, please run like that:\n"\
        "	./ddrbin_tool px30 -g gen_param.txt px30_ddr_333MHz_v1.15.bin\n"\
        "	The config will show in gen_param.txt.\n"\
        "\n"\
        "Note:	The function 1 and function 2 are two separate functions\n"\
        "The gen_param.txt file which is generated by function 2 is no need used in function 1.\n"\
        "\n"\
        "For more details, please refer to the ddrbin_tool_user_guide.txt\n"\
    )


def ddrbin_tool(argc, argv):
    global updata_key_list
    global chip_info

    info_from_txt = copy.deepcopy(base_info_full)
    info_from_bin = copy.deepcopy(base_info_full)
    ddrbin_index = copy.deepcopy(sdram_head_info_index_v2)

    version_old_hit = 0
    gen_txt_from_bin = 0

    verinfo_full = ''
    verinfo_full_offset = 0
    verinfo_full_length = 0
    verinfo_editable = ''
    verinfo_editable_offset = 0
    verinfo_editable_length = 17

    print("version v1.21 20241211")
    print("python {}, {}, {}".format(sys.version.split(' ', 1)[0], platform.system(), platform.machine()))
    if sys.version_info < (3, 6):
        print("Warning: Please installed Python 3.6 or later.")

    if argc == 1:
        print_help()
        return -1

    chip_info = argv[1]
    if chip_info not in chip_list:
        chip_info = 'others chip'
    print("chip: {}".format(chip_info))

    try:
        opts, args = getopt.gnu_getopt(argv, 'g:h', ['verinfo_editable='])
    except:
        print_help()
        return -1

    for opt, arg in opts:
        if opt == '-g':
            gen_txt_from_bin = 1
            filegen_path = arg
        elif opt == '--verinfo_editable':
            verinfo_editable = arg
            if len(verinfo_editable) > verinfo_editable_length:
                print("The character count of 'verinfo_editable' exceeds the allowed limit of 17.")
                return -1
        elif opt == '-h':
            print_help()
            return -1

    if gen_txt_from_bin == 1:
        # function: get ddr.bin file config to gen_param.txt file
        if argc < 5:
            print("The number of parameters error")
            print_help()
            return -1

        filebin_path = argv[4]
        if os.path.exists(filebin_path) != True:
            print("The file {} not exist".format(filebin_path))
            return -1

        #print(f"D: filegen_path={filegen_path}, {filebin_path}")
    else:
        # function: modify ddr.bin file from ddrbin_param.txt.
        if argc < 4:
            print("The number of parameters error")
            print_help()
            return -1

        fileskew_path = argv[2]
        if os.path.exists(fileskew_path) != True:
            print("The file {} not exist".format(fileskew_path))
            return -1

        filebin_path = argv[3]
        if os.path.exists(filebin_path) != True:
            print("The file {} not exist".format(filebin_path))
            return -1

        for key in version_old_list:
            if key in argv[3]:
                version_old_hit = 1
        #print(f"D: fileskew_path={fileskew_path},{filebin_path},version_old_hit={version_old_hit}")

    if gen_txt_from_bin != 1:
        # Read the parameters that need to be modified from the txt file.
        key_list = list(info_from_txt.keys())
        hot = 0
        try:
            with open(fileskew_path,'r', encoding='UTF-8') as file:
                for line in file:
                    if '/*' in line:
                        continue

                    if '=' in line:
                        index_of_line = line.find('=')
                        if line[index_of_line : ].strip() != '=':
                            info_dict_key = line[ : index_of_line]
                            info_dict_value = line[index_of_line + 1 : -1]

                            if '0x' in info_dict_value:
                                info_dict_value = int(info_dict_value[2:], 16)
                            else:
                                info_dict_value = int(info_dict_value)

                            info_from_txt[info_dict_key]['value'] = info_dict_value

                            # append info_dict_key to update_key_list, need updata value from txt
                            update_key_list.append(info_dict_key)
                            #print(f"D: update_key_list append, {info_dict_key}={info_dict_value}")

                        hot = hot + 1
        except (KeyError, ValueError):
            print("KeyError or ValueError: {}={}".format(info_dict_key, info_dict_value))
            return -1
        except Exception:
            print("The file {} read failed".format(fileskew_path))
            return -1

        if hot == 0:
            print("Failed to read DRAM parameters from the file")
            return -1
    else:
        info_from_txt['start tag']['value'] = 0x12345678

    # get info from bin file
    with open(filebin_path, 'rb') as file:
        content = file.read()
    # convert the target byte sequence 'start tag' into bytes, byteorder little
    target_bytes = struct.pack('<I', info_from_txt['start tag']['value'])
    start_position = 0
    while True:
        position = content.find(target_bytes, start_position)
        if position == -1:
            break

        version = int.from_bytes(content[position + 4: position + 8], byteorder='little')
        if version >= 0 and version <= version_max:
            break
        else:
            start_position = position + len(target_bytes)

    if position == -1:
        if start_position == 0:
            print("Find the 'start tag' in the ddrbin file failed")
        else:
            print("version = {}, invalid.".format(version))
            if version > version_max and version < (version_max + 5):
                print("Please check if there is a new version of the tool available.")
        return -1

    # get ddrbin parameters version
    try:
        bin_skew_offset = position + 4
        filebin = open(filebin_path, 'rb+')
        filebin.seek(bin_skew_offset)
        version = int.from_bytes(filebin.read(4), byteorder='little')
    except:
        print("get version fail")
        filebin.close()
        return -1

    print("version {}".format(version))

    # get ddrbin version information from bin file
    # eg: DDR 03ea844c5d typ 24/09/03-10:42:57,fwver: v1.23
    target_bytes = b'DDR '
    target_bytes_1 = b',fwver:'
    start_position = 0
    while True:
        position = content.find(target_bytes, start_position)
        position_1 = content.find(target_bytes_1, start_position)
        if position == -1 or position_1 == -1:
            break
        elif (position_1 - position) < 100:
            verinfo_full = content[position: position_1+30].decode('utf-8', errors='replace')
            verinfo_full = verinfo_full[:verinfo_full.find('\n')]
            if content[position_1 - verinfo_editable_length - 1].to_bytes(1, 'little') == b' ':
                verinfo_editable_offset = position_1 - verinfo_editable_length
                verinfo_full_offset = position
                verinfo_full_length = len(verinfo_full.encode('utf-8'))
                print("{}".format(verinfo_full))
                break
        else:
            start_position = position + len(target_bytes)

    if version < 2:
        read_out = copy.deepcopy(sdram_head_info_v0)
        write_in = copy.deepcopy(sdram_head_info_v0)

        # skip gcpu_gen_freq after version_info
        filebin.seek(bin_skew_offset + 8)
    elif version <= 5:
        if version >= 3:
            ddrbin_index.update(sdram_head_info_index_v2_3)
        if version >= 4:
            ddrbin_index.update(sdram_head_info_index_v3_4)

        if version < 5:
            read_out = copy.deepcopy(sdram_head_info_v2)
            write_in = copy.deepcopy(sdram_head_info_v2)
        else:
            read_out = copy.deepcopy(sdram_head_info_v5)
            write_in = copy.deepcopy(sdram_head_info_v5)

        #index_info read out
        for key in ddrbin_index:
            try:
                ddrbin_index[key]['offset'] = int.from_bytes(filebin.read(1), byteorder='little')
                ddrbin_index[key]['size'] = int.from_bytes(filebin.read(1), byteorder='little')
            except:
                filebin.close()
                print("readout ddrbin_index fail")
                return -1
            #print(f"D: {key} = {index[key]}",ddrbin_index[key]["offset"],ddrbin_index[key]["size"])
    else:
        filebin.close()
        print("version not support")
        return -1

    if bin_data_readout(filebin, ddrbin_index, read_out, bin_skew_offset, version, info_from_txt) != 0:
        filebin.close()
        print("bin_data_readout failed")
        return -1

    bin_data_2_info(info_from_bin, read_out, ddrbin_index, version, info_from_txt)
    if gen_txt_from_bin == 1:
        if gen_info_from_bin(filegen_path, info_from_bin, verinfo_full, version) == 0:
            print("generate info from bin file ok.")
            filebin.close()
            return 0
        else:
            print("generate info fail.")
            filebin.close()
            return -1

    txt_data_2_bin_data(info_from_txt, info_from_bin, ddrbin_index, write_in, version)

    if version < 2:
        if version_old_hit == 0:
            filebin.seek(bin_skew_offset + 8)
            for i in range(len(write_in)):
                try:
                    filebin.write(write_in[i][1].to_bytes(4,byteorder='little'))
                except:
                    print("write bin file fail")
        else:
            filebin.seek(bin_skew_offset + 20)
            for i in range(3, len(write_in)):
                try:
                    filebin.write(write_in[i][1].to_bytes(4,byteorder='little'))
                except:
                    print("write bin file fail")
    elif version <= version_max:
        write_in_bin_data_v2(filebin, bin_skew_offset, write_in, ddrbin_index, info_from_txt, version)
    print("modify end\n")

    # update ddrbin version information to bin file
    if verinfo_editable_offset != 0:
        if verinfo_editable == '':
            #print(f"position_1={position_1}, position_2={position_2}, {old_verinfo_editable}")
            current_time = datetime.now()
            verinfo_editable = current_time.strftime("%y/%m/%d-%H:%M.%S")
        if len(verinfo_editable) < verinfo_editable_length:
            verinfo_editable = verinfo_editable.ljust(verinfo_editable_length)

        verinfo_editable_bytes = verinfo_editable.encode('utf-8')[:verinfo_editable_length]
        try:
            filebin.seek(verinfo_editable_offset)
            filebin.write(verinfo_editable_bytes)
            filebin.seek(verinfo_full_offset)
            new_verinfo_full = filebin.read(verinfo_full_length).decode('utf-8', errors='replace')
            print("new ddrbin version information: {}".format(new_verinfo_full))
        except:
            print("change verinfo_editable error")

    filebin.close()

    return 0


if __name__ == '__main__':
    #print(f"D: argc = {len(sys.argv)}, argv = {sys.argv}")
    ddrbin_tool(len(sys.argv), sys.argv)

