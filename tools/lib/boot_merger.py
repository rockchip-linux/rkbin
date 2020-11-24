# -*- coding: utf-8 -*-
"""
name: boot_merger
date:2018.02.25
author: seth
description: pack and unpack loader
usage of generating loader:
boot_merger pack <--chip> <--loader_ver> <--471_entry 1..n> <--472_entry 1..n> <--loader_data> <--loader_code> [--rc4_off] <--output>
arguments:
--chip          chip id  e.g. RK3399,RK330D
--loader_ver    loader version xx.xx
--entry_471     471 entrys ddr.bin
--entry_472     472 entrys usbplug.bin
--loader_data   flashdata.bin
--loader_code   flashboot.bin
--rc4_off       loader data and code without rc4 encryption  [option]
--output        path of new rk loader
boot_merger pack <inifile>
inifile format:
[CHIP_NAME]
NAME=RK330A
[VERSION]
MAJOR=1
MINOR=0
[CODE471_OPTION]
NUM=1
Path1=ddr.bin
[CODE472_OPTION]
NUM=1
Path1=usbplug.bin
[LOADER_OPTION]
NUM=2
FlashData=FlashData.bin
FlashBoot=FlashBoot.bin
[OUTPUT]
PATH=RK3026Loader.bin
[FLAG]
RC4_OFF=

usage of unpacking loader:
boot_merger unpack <--loader> <--output>
arguments:
--loader       rk loader
--output       output dir for saving files
"""
import argparse, sys, os, struct, datetime, io, platform, re, configparser, string,subprocess
#import  numpy as np
from timeit import default_timer as timer
from rk_mod import crc32,rc4
from Crypto.Hash import SHA256,SHA512
# from crcmod import crc32
# from crcmod import rc4
APP_VERSION = '%(prog)s v1.31'
RKNONE_DEVICE = 0
RK27_DEVICE = 0x10
RKCAYMAN_DEVICE = 0x11
RK28_DEVICE = 0x20
RK281X_DEVICE = 0x21
RKPANDA_DEVICE = 0x22
RKNANO_DEVICE = 0x30
RKSMART_DEVICE = 0x31
RKCROWN_DEVICE = 0x40
RK29_DEVICE = 0x50
RK292X_DEVICE = 0x51
RK30_DEVICE = 0x60
RK30B_DEVICE = 0x61
RK31_DEVICE = 0x70
RK32_DEVICE = 0x80
SECTOR_SIZE = 512
PAGE_SIZE = 2048
ENTRY471 = 1
ENTRY472 = 2
ENTRYLOADER = 4
NEW_IDB_SMALL = '<I4sII8s8s88sIIII8s64sIIII8s64sIIII8s64sIIII8s64s40s'
NEW_IDB = NEW_IDB_SMALL + '512s16s32s464s512s'
def align(size, unit):
    size = size + unit - 1
    size = size & (~(unit - 1))
    return size

# CRC32_FACTOR = 0x04C10DB7
# gTable_Crc32 =[
# 		0x00000000, 0x04c10db7, 0x09821b6e, 0x0d4316d9,
# 		0x130436dc, 0x17c53b6b, 0x1a862db2, 0x1e472005,
# 		0x26086db8, 0x22c9600f, 0x2f8a76d6, 0x2b4b7b61,
# 		0x350c5b64, 0x31cd56d3, 0x3c8e400a, 0x384f4dbd,
# 		0x4c10db70, 0x48d1d6c7, 0x4592c01e, 0x4153cda9,
# 		0x5f14edac, 0x5bd5e01b, 0x5696f6c2, 0x5257fb75,
# 		0x6a18b6c8, 0x6ed9bb7f, 0x639aada6, 0x675ba011,
# 		0x791c8014, 0x7ddd8da3, 0x709e9b7a, 0x745f96cd,
# 		0x9821b6e0, 0x9ce0bb57, 0x91a3ad8e, 0x9562a039,
# 		0x8b25803c, 0x8fe48d8b, 0x82a79b52, 0x866696e5,
# 		0xbe29db58, 0xbae8d6ef, 0xb7abc036, 0xb36acd81,
# 		0xad2ded84, 0xa9ece033, 0xa4aff6ea, 0xa06efb5d,
# 		0xd4316d90, 0xd0f06027, 0xddb376fe, 0xd9727b49,
# 		0xc7355b4c, 0xc3f456fb, 0xceb74022, 0xca764d95,
# 		0xf2390028, 0xf6f80d9f, 0xfbbb1b46, 0xff7a16f1,
# 		0xe13d36f4, 0xe5fc3b43, 0xe8bf2d9a, 0xec7e202d,
# 		0x34826077, 0x30436dc0, 0x3d007b19, 0x39c176ae,
# 		0x278656ab, 0x23475b1c, 0x2e044dc5, 0x2ac54072,
# 		0x128a0dcf, 0x164b0078, 0x1b0816a1, 0x1fc91b16,
# 		0x018e3b13, 0x054f36a4, 0x080c207d, 0x0ccd2dca,
# 		0x7892bb07, 0x7c53b6b0, 0x7110a069, 0x75d1adde,
# 		0x6b968ddb, 0x6f57806c, 0x621496b5, 0x66d59b02,
# 		0x5e9ad6bf, 0x5a5bdb08, 0x5718cdd1, 0x53d9c066,
# 		0x4d9ee063, 0x495fedd4, 0x441cfb0d, 0x40ddf6ba,
# 		0xaca3d697, 0xa862db20, 0xa521cdf9, 0xa1e0c04e,
# 		0xbfa7e04b, 0xbb66edfc, 0xb625fb25, 0xb2e4f692,
# 		0x8aabbb2f, 0x8e6ab698, 0x8329a041, 0x87e8adf6,
# 		0x99af8df3, 0x9d6e8044, 0x902d969d, 0x94ec9b2a,
# 		0xe0b30de7, 0xe4720050, 0xe9311689, 0xedf01b3e,
# 		0xf3b73b3b, 0xf776368c, 0xfa352055, 0xfef42de2,
# 		0xc6bb605f, 0xc27a6de8, 0xcf397b31, 0xcbf87686,
# 		0xd5bf5683, 0xd17e5b34, 0xdc3d4ded, 0xd8fc405a,
# 		0x6904c0ee, 0x6dc5cd59, 0x6086db80, 0x6447d637,
# 		0x7a00f632, 0x7ec1fb85, 0x7382ed5c, 0x7743e0eb,
# 		0x4f0cad56, 0x4bcda0e1, 0x468eb638, 0x424fbb8f,
# 		0x5c089b8a, 0x58c9963d, 0x558a80e4, 0x514b8d53,
# 		0x25141b9e, 0x21d51629, 0x2c9600f0, 0x28570d47,
# 		0x36102d42, 0x32d120f5, 0x3f92362c, 0x3b533b9b,
# 		0x031c7626, 0x07dd7b91, 0x0a9e6d48, 0x0e5f60ff,
# 		0x101840fa, 0x14d94d4d, 0x199a5b94, 0x1d5b5623,
# 		0xf125760e, 0xf5e47bb9, 0xf8a76d60, 0xfc6660d7,
# 		0xe22140d2, 0xe6e04d65, 0xeba35bbc, 0xef62560b,
# 		0xd72d1bb6, 0xd3ec1601, 0xdeaf00d8, 0xda6e0d6f,
# 		0xc4292d6a, 0xc0e820dd, 0xcdab3604, 0xc96a3bb3,
# 		0xbd35ad7e, 0xb9f4a0c9, 0xb4b7b610, 0xb076bba7,
# 		0xae319ba2, 0xaaf09615, 0xa7b380cc, 0xa3728d7b,
# 		0x9b3dc0c6, 0x9ffccd71, 0x92bfdba8, 0x967ed61f,
# 		0x8839f61a, 0x8cf8fbad, 0x81bbed74, 0x857ae0c3,
# 		0x5d86a099, 0x5947ad2e, 0x5404bbf7, 0x50c5b640,
# 		0x4e829645, 0x4a439bf2, 0x47008d2b, 0x43c1809c,
# 		0x7b8ecd21, 0x7f4fc096, 0x720cd64f, 0x76cddbf8,
# 		0x688afbfd, 0x6c4bf64a, 0x6108e093, 0x65c9ed24,
# 		0x11967be9, 0x1557765e, 0x18146087, 0x1cd56d30,
# 		0x02924d35, 0x06534082, 0x0b10565b, 0x0fd15bec,
# 		0x379e1651, 0x335f1be6, 0x3e1c0d3f, 0x3add0088,
# 		0x249a208d, 0x205b2d3a, 0x2d183be3, 0x29d93654,
# 		0xc5a71679, 0xc1661bce, 0xcc250d17, 0xc8e400a0,
# 		0xd6a320a5, 0xd2622d12, 0xdf213bcb, 0xdbe0367c,
# 		0xe3af7bc1, 0xe76e7676, 0xea2d60af, 0xeeec6d18,
# 		0xf0ab4d1d, 0xf46a40aa, 0xf9295673, 0xfde85bc4,
# 		0x89b7cd09, 0x8d76c0be, 0x8035d667, 0x84f4dbd0,
# 		0x9ab3fbd5, 0x9e72f662, 0x9331e0bb, 0x97f0ed0c,
# 		0xafbfa0b1, 0xab7ead06, 0xa63dbbdf, 0xa2fcb668,
# 		0xbcbb966d, 0xb87a9bda, 0xb5398d03, 0xb1f880b4]
RK_LOADER_ENTRY_FORMAT = ('<B'  # struct size
                          'i'  # entry type
                          '20H'  # name wstring
                          '3I')  # offset,size,delay
BOOT_TAG = 0x544F4F42
LDR_FORMAT_VER = 0x1000000
LDR_TAG = 0x2052444C
SECURE_TAG = 0x4B415352
RK_LOADER_HEAD_FORMAT = ('<I'  # tag:BOOT
                         'H'  # struct size
                         '2I'  # version
                         '7s'  # release time
                         'i'  # support chip
                         'B'  # 471 count
                         'I'  # 471 offset
                         'B'  # 471 entry size
                         'B'  # 472 count
                         'I'  # 472 offset
                         'B'  # 472 entry size
                         'B'  # loader count
                         'I'  # loader offset
                         'B'  # loader entry size
                         '3B' # sign flag,rc4 flag,471 rc4 flag
                         '56s') #reserved
# def do_crc32(buf,size):
#     crc = 0
#     for data in buf[0:size]:
#         crc = ((crc << 8) & 0xFFFFFF00) ^ gTable_Crc32[((crc >> 24) & 0xFF) ^ data]
#     return crc


# def rc4(buf):
#     size = len(buf)
#     buf = bytearray(buf)
#     key = np.uint8([124, 78, 3, 4, 85, 5, 9, 7, 45, 44, 123, 56, 23, 13, 23, 17])
#     S = np.zeros(256, dtype=np.uint8)
#     K = np.zeros(256, dtype=np.uint8)
#     t = np.uint8(0)
#     i = j = x = 0
#     for i in range(256):
#         S[i] = np.uint8(i)
#         j = j & 0xF
#         K[i] = key[j]
#         j = j + 1
#
#     j = 0
#     for i in range(256):
#         j = (j + S[i] + K[i]) % 256
#         t = S[i]
#         S[i] = S[j]
#         S[j] = t
#
#     i = j = 0
#     for x in range(size):
#         i = (i + 1) % 256
#         j = (j + S[i]) % 256
#         S[i],S[j] = S[j],S[i]
#         # t = S[i]
#         # S[i] = S[j]
#         # S[j] = t
#         t = (S[i] + (S[j] % 256)) % 256
#         buf[x] = np.uint8(buf[x]) ^ S[t]
#     return buf
def usage():
    print("boot_merger is a tool for generating rkloader and extracting sources from rkloader")
    print("generate rkloader: boot_merger pack [args..] //input \'boot_merger pack --help\' to get details")
    print("extract rkloader: boot_merger unpack [args..] //input \'boot_merger unpack --help\' to get details")
    print("change version: boot_merger change_ver [args..] //change loader version")
    print("insert CA: boot_merger ins_cert [args..] //insert CA cert into flashhead part")
    print("delete CA: boot_merger del_cert [args..] //delete CA cert from flashhead part")
def do_sha256(message, digest, init=None):
    try:
        sha_obj = init
        if sha_obj is None:
            sha_obj = SHA256.new()
        blk_size = sha_obj.block_size
        msg_size = len(message)
        update_size = 0
        pos = 0
        while msg_size > 0 :
            if msg_size >= blk_size:
                update_size = blk_size
            else:
                update_size = msg_size
            sha_obj.update(message[pos:pos+update_size])
            pos += update_size
            msg_size -= update_size

        digest[:] = sha_obj.digest()
        return True
    except Exception as e:
        print("error:%s" % str(e))
    return False
def do_sha512(message, digest, init=None):
    try:
        sha_obj = init
        if sha_obj is None:
            sha_obj = SHA512.new()
        blk_size = sha_obj.block_size
        msg_size = len(message)
        update_size = 0
        pos = 0
        while msg_size > 0 :
            if msg_size >= blk_size:
                update_size = blk_size
            else:
                update_size = msg_size
            sha_obj.update(message[pos:pos+update_size])
            pos += update_size
            msg_size -= update_size

        digest[:] = sha_obj.digest()
        return True
    except Exception as e:
        print("error:%s" % str(e))
    return False
def create_new_idblock(in_files,keep_cert,hash_type,out_image):
    idb_size = struct.calcsize(NEW_IDB)
    idb = bytearray(idb_size)
    idb_list = list(struct.unpack(NEW_IDB, idb))

    idb_list[0] = 0x534E4B52  # RKNS
    idb_list[2] = len(in_files) << 16
    idb_list[2] += 384
    if hash_type.upper() == 'SHA256':
        idb_list[3] += 1
    elif hash_type.upper() == 'SHA512':
        idb_list[3] += 2
    if not keep_cert:
        image_offset = 4
    else:
        image_offset = 8
    file_data_list = list()
    for i, file in enumerate(in_files):
        file_size = os.path.getsize(file)
        image_sector = align(file_size, PAGE_SIZE) // SECTOR_SIZE
        idb_list[7 + i * 6] = (image_sector << 16) + image_offset
        idb_list[8 + i * 6] = 0xFFFFFFFF
        idb_list[10 + i * 6] = i + 1
        idb_list[12 + i * 6] = bytearray(idb_list[12 + i * 6])
        with open(file, 'rb') as fin:
            file_data = bytearray(fin.read())
        file_data = file_data.ljust(image_sector * SECTOR_SIZE, b'\0')
        file_data_list.append(file_data)
        if hash_type.upper() == 'SHA256':
            digest = bytearray(32)
            do_sha256(file_data, digest)
            idb_list[12 + i * 6][0:32] = digest
        elif hash_type.upper() == 'SHA512':
            do_sha512(file_data, idb_list[12 + i * 6])
        image_offset += image_sector
    idb = bytearray(struct.pack(NEW_IDB, *idb_list))

    digest = bytearray(64)
    if hash_type.upper() == 'SHA256':
        do_sha256(idb[:-512], digest)
    elif hash_type.upper() == 'SHA512':
        do_sha512(idb[:-512], digest)
    idb[-512:-512 + len(digest)] = digest

    with open(out_image, 'wb') as fout:
        fout.write(idb)

def convert_chip(chip):
    value = 0
    chip_string = chip
    if (len(chip_string) < 4) or (len(chip_string) > 6):
        return -1
    head = chip_string[0:2]
    if (head.lower() != "rk") and (head.lower() != "rv"):
        return -1
    chip_string = chip_string[2:]
    if chip_string.lower() == "28":
        value = RK28_DEVICE
    elif chip_string.lower() == "281x":
        value = RK281X_DEVICE
    elif chip_string.lower() == "panda":
        value = RKPANDA_DEVICE
    elif chip_string.lower() == "27":
        value = RK27_DEVICE
    elif chip_string.lower() == "nano":
        value = RKNANO_DEVICE
    elif chip_string.lower() == "smart":
        value = RKSMART_DEVICE
    elif chip_string.lower() == "crown":
        value = RKCROWN_DEVICE
    elif chip_string.lower() == "cayman":
        value = RKCAYMAN_DEVICE
    elif chip_string.lower() == "29":
        value = RK29_DEVICE
    elif chip_string.lower() == "292x":
        value = RK292X_DEVICE
    elif chip_string.lower() == "30":
        value = RK30_DEVICE
    elif chip_string.lower() == "30b":
        value = RK30B_DEVICE
    elif chip_string.lower() == "31":
        value = RK31_DEVICE
    elif chip_string.lower() == "32":
        value = RK32_DEVICE
    else:
        j = 0
        for i,ch in enumerate(chip_string):
            value += ord(ch)
            if i < 3:
                value <<= 8
            j = j + 1
        while j < 3:
            value <<= 8
            j = j + 1
    return value & 0xFFFFFFFF
def is_hex_string(str):
    return all(s in string.hexdigits for s in str)
def convert_loader_ver(ver):
    ver_value = ver.split('.')
    if len(ver_value) != 2:
        return -1
    if not (is_hex_string(ver_value[0]) and is_hex_string(ver_value[1])):
        return -1
    loader_ver = int(ver_value[0], 10)
    loader_ver = loader_ver << 8
    loader_ver += int(ver_value[1], 10)
    return loader_ver & 0xFFFFFFFF
def boot_merger_main():
    total_start = timer()
    major = sys.version_info[0]
    minor = sys.version_info[1]
    small = sys.version_info[2]
    ver = major * 100 + minor * 10 + small
    if ver < 300:
        print("Error:script can not run in python2")
        return
    argc = len(sys.argv)
    if argc > 1:
        cmd = sys.argv[1];
        if cmd.lower() not in ['pack','unpack','change_ver','ins_cert','del_cert']:
            cmd = 'pack'
            sys.argv.insert(1,'pack')
            argc=argc+1
        if cmd.lower() == "pack":
            input_from_ini = False
            need_create_head = False
            curr_head_tag = BOOT_TAG
            keep_sec_cert = False
            hash_type = 'sha256'
            in_chip_str = ''
            in_verion_str = ''
            in_entry471 = list()
            in_entry472 = list()
            in_loader_entry = list()
            entry_loader_name = ['FlashData','FlashBoot','FlashHead']
            in_rc4_flag = 0
            in_471_rc4 = 0
            in_output = ''
            if argc == 3:
                ini_param = sys.argv[2]
                if os.path.exists(ini_param):
                    ini_base_name = os.path.basename(ini_param)
                    if bool(re.search(r'\.ini$', ini_base_name, re.IGNORECASE)):
                        try:
                            ini_obj = configparser.ConfigParser()
                            ini_obj.read(ini_param)
                            in_chip_str = ini_obj.get('CHIP_NAME','NAME')
                            ini_major = ini_obj.get('VERSION', 'MAJOR')
                            ini_minor = ini_obj.get('VERSION', 'MINOR')
                            in_verion_str = ini_major + '.' + ini_minor
                            ini_471_num = ini_obj.getint('CODE471_OPTION', 'NUM')
                            ini_472_num = ini_obj.getint('CODE472_OPTION', 'NUM')
                            ini_loader_num = ini_obj.getint('LOADER_OPTION', 'NUM')
                            for i in range(ini_471_num):
                                file_entry471 = ini_obj.get('CODE471_OPTION', 'Path'+str(i+1))
                                in_entry471.append(file_entry471)
                            for i in range(ini_472_num):
                                file_entry472 = ini_obj.get('CODE472_OPTION', 'Path'+str(i+1))
                                in_entry472.append(file_entry472)
                            if ini_loader_num:
                                if ini_obj.has_option('LOADER_OPTION','FlashData'):
                                    in_loader_data = ini_obj.get('LOADER_OPTION', 'FlashData')
                                    in_loader_entry.append(in_loader_data)
                                if ini_obj.has_option('LOADER_OPTION', 'FlashBoot'):
                                    in_loader_code = ini_obj.get('LOADER_OPTION', 'FlashBoot')
                                    in_loader_entry.append(in_loader_code)
                                if ini_obj.has_option('LOADER_OPTION','FlashHead'):
                                    in_loader_head = ini_obj.get('LOADER_OPTION', 'FlashHead')
                                    in_loader_entry.append(in_loader_head)
                            in_output = ini_obj.get('OUTPUT', 'PATH')
                            if ini_obj.has_option('FLAG', 'RC4_OFF'):
                                ini_rc4_flag = ini_obj.get('FLAG', 'RC4_OFF')
                                ini_rc4_flag.lower()
                                if ini_rc4_flag == '1' or ini_rc4_flag == 'true':
                                    in_rc4_flag = 1
                            if ini_obj.has_option('FLAG', '471_RC4_OFF'):
                                ini_rc4_flag = ini_obj.get('FLAG', '471_RC4_OFF')
                                ini_rc4_flag.lower()
                                if ini_rc4_flag == '1' or ini_rc4_flag == 'true':
                                    in_471_rc4 = 1
                            if ini_obj.has_section('SYSTEM'):
                                if ini_obj.has_option('SYSTEM','NEWIDB'):
                                    try:
                                        if ini_obj.getboolean('SYSTEM','NEWIDB'):
                                            need_create_head = True
                                    except ValueError as e:
                                        pass
                                if ini_obj.has_option('SYSTEM','KEEPCERT'):
                                    try:
                                        if ini_obj.getboolean('SYSTEM','KEEPCERT'):
                                            keep_sec_cert = True
                                    except ValueError as e:
                                        pass
                                if ini_obj.has_option('SYSTEM','HASHTYPE'):
                                    try:
                                        temp = ini_obj.get('SYSTEM','HASHTYPE')
                                        if temp.lower() in ['sha256','sha512']:
                                            hash_type = temp
                                    except ValueError as e:
                                        pass
                            input_from_ini = True
                        except Exception as e:
                            print("read ini exception,%s!" % str(e))
                            return
            if not input_from_ini:
                parser = argparse.ArgumentParser(description='pack rk loader tool', prog='boot_merger pack')
                parser.add_argument('--version', action='version', version=APP_VERSION)
                parser.add_argument('--chip', nargs=1, help='chip id like as RK330A')
                parser.add_argument('--loader_ver', nargs=1, help='version like as xx.xx')
                parser.add_argument('--entry_471', nargs='+', help='usually ddr init code')
                parser.add_argument('--entry_472', nargs='+', help='usually usbplug')
                parser.add_argument('--entry_loader',nargs='+', help='usually flashdata flashboot flashhead')
                parser.add_argument('--create_head', action='store_true', help='create head for new idb')
                parser.add_argument('--rc4_off', action='store_true', help='close loader rc4')
                parser.add_argument('--rc4_471_off', action='store_true', help='close 471 rc4')
                parser.add_argument('--keep_cert', action='store_true', help='keep cert reserved')
                parser.add_argument('--hash_type', choices=['sha256','sha512'], help='hash for new idb')
                parser.add_argument('--output', nargs=1, help='loader filepath')
                args = parser.parse_args(sys.argv[2:])
                in_chip_str = args.chip[0]
                in_verion_str = args.loader_ver[0]
                in_entry471 = args.entry_471
                in_entry472 = args.entry_472
                in_loader_entry = args.entry_loader
                if not args.rc4_off:
                    in_rc4_flag = 0
                else:
                    in_rc4_flag = 1
                if not args.rc4_471_off:
                    in_471_rc4 = 0
                else:
                    in_471_rc4 = 1

                if not args.keep_cert:
                    pass
                else:
                    keep_sec_cert = True
                if not args.hash_type:
                    pass
                else:
                    hash_type = args.hash_type

                if not args.create_head:
                    pass
                else:
                    need_create_head = True
                in_output = args.output[0]
            if need_create_head:
                out_usb_head = os.path.join(os.path.dirname(in_entry471[0]), 'UsbHead.bin')
                if os.path.exists(out_usb_head):
                    os.unlink(out_usb_head)
                # start = timer()
                create_new_idblock([in_entry471[0],in_entry472[0]],keep_sec_cert,hash_type,out_usb_head)
                # print('create usb head elapsed:%.2f' % (timer() - start))
                if not os.path.isfile(out_usb_head):
                    print("Failed to create %s" % out_usb_head)
                    return
                out_flash_head = os.path.join(os.path.dirname(in_loader_entry[0]), 'FlashHead.bin')
                if os.path.exists(out_flash_head):
                    os.unlink(out_flash_head)
                # start = timer()
                create_new_idblock(in_loader_entry[0:2],keep_sec_cert,hash_type,out_flash_head)
                # print('create flash head elapsed:%.2f' % (timer() - start))
                if not os.path.isfile(out_flash_head):
                    print("Failed to create %s" % out_flash_head)
                    return
                in_entry471.insert(0,out_usb_head)
                in_loader_entry.insert(2,out_flash_head)
            '''
            print("chip=%s" % args.chip)
            print("ver=%s" % args.loader_ver)
            print("471 coutn=%d item=%s" % (len(args.entry_471), args.entry_471[0]))
            print("472 count=%d item=%s" % (len(args.entry_472), args.entry_472[0]))
            print("loader_data=%s" % args.entry_loader[0])
            print("loader_code=%s" % args.entry_loader[1])
            print("rc4_off=%d" % args.rc4_off)
            print("output=%s" % args.output)
          '''
            if len(in_loader_entry)>3:
                print('loader entry must be <= 3.')
                return
            if not input_from_ini:
                print("packing loader start...")
            loader_chip = convert_chip(in_chip_str)
            if loader_chip == -1:
                print("invalid chip %s" % in_chip_str)
                return
            loader_ver = convert_loader_ver(in_verion_str)
            if loader_ver == -1:
                print("invalid loader ver %s" % in_verion_str)
                return
            #1.fill up loader head
            if need_create_head or len(in_loader_entry)>2:
                curr_head_tag = LDR_TAG
            loader_head_size = struct.calcsize(RK_LOADER_HEAD_FORMAT)
            loader_head_buf = bytearray(loader_head_size)
            # loader_head_buf[0:] = [0 for i in range(loader_head_size)]
            loader_head_struct = list(struct.unpack(RK_LOADER_HEAD_FORMAT, loader_head_buf))
            loader_head_struct[0] = curr_head_tag
            loader_head_struct[3] = LDR_FORMAT_VER
            loader_head_struct[1] = loader_head_size
            loader_head_struct[2] = loader_ver
            # loader_head_struct[3] = 0
            release_time_struct = list(struct.unpack('H5B', loader_head_struct[4][:]))
            release_time = datetime.datetime.now()
            release_time_struct[0] = release_time.year
            release_time_struct[1] = release_time.month
            release_time_struct[2] = release_time.day
            release_time_struct[3] = release_time.hour
            release_time_struct[4] = release_time.minute
            release_time_struct[5] = release_time.second
            loader_head_struct[4] = struct.pack('H5B', *release_time_struct)
            loader_head_struct[5] = loader_chip
            count_471 = len(in_entry471)
            count_472 = len(in_entry472)
            count_loader = len(in_loader_entry)
            loader_entry_size = struct.calcsize(RK_LOADER_ENTRY_FORMAT)
            loader_head_struct[6] = count_471
            loader_head_struct[7] = loader_head_size #471 entry offset
            loader_head_struct[8] = loader_entry_size
            loader_head_struct[9] = count_472
            loader_head_struct[10] = loader_head_struct[7] + count_471 * loader_entry_size #472 entry offset
            loader_head_struct[11] = loader_entry_size
            loader_head_struct[12] = count_loader
            loader_head_struct[13] = loader_head_struct[10] + count_472 * loader_entry_size  # loader entry offset
            loader_head_struct[14] = loader_entry_size
            for file in in_loader_entry:
                with open(file,'rb') as fp:
                    sign = fp.read(4)
                    tag = int.from_bytes(sign[0:4], 'little')
                    if tag == SECURE_TAG or tag == 0x53534B52:
                        loader_head_struct[15] = ord('S')

            loader_head_struct[16] = in_rc4_flag
            loader_head_struct[17] = in_471_rc4
            loader_head_buf = struct.pack(RK_LOADER_HEAD_FORMAT, *loader_head_struct)
            # print("writing head...")
            fout = open(in_output, 'wb+')
            fout.write(loader_head_buf)
            #2.fill up entry
            if not input_from_ini:
                print("writing entry...")
            data_offset = loader_head_size + (count_471 + count_472 + count_loader) * loader_entry_size
            loader_entry_buf = bytearray(loader_entry_size)
            loader_entry_struct = list(struct.unpack(RK_LOADER_ENTRY_FORMAT, loader_entry_buf))
            loader_entry_struct[0] = loader_entry_size
            loader_entry_struct[1] = ENTRY471
            for i in range(count_471):
                item_name = in_entry471[i]
                if not os.path.exists(item_name):
                    print("%s is not existed" % item_name)
                    fout.close()
                    return
                item_size = os.path.getsize(item_name)
                item_name = os.path.basename(item_name).split('.')[0]
                for j in range(20):
                    if j < len(item_name):
                        loader_entry_struct[2 + j] = ord(item_name[j])
                    else:
                        loader_entry_struct[2 + j] = 0
                loader_entry_struct[22] = data_offset
                loader_entry_struct[23] = align(item_size,PAGE_SIZE)
                data_offset += loader_entry_struct[23]
                loader_entry_buf = struct.pack(RK_LOADER_ENTRY_FORMAT, *loader_entry_struct)
                fout.write(loader_entry_buf)
            loader_entry_struct[1] = ENTRY472
            for i in range(count_472):
                item_name = in_entry472[i]
                if not os.path.exists(item_name):
                    print("%s is not existed" % item_name)
                    fout.close()
                    return
                item_size = os.path.getsize(item_name)
                item_name = os.path.basename(item_name).split('.')[0]
                for j in range(20):
                    if j < len(item_name):
                        loader_entry_struct[2 + j] = ord(item_name[j])
                    else:
                        loader_entry_struct[2 + j] = 0
                loader_entry_struct[22] = data_offset
                loader_entry_struct[23] = align(item_size, PAGE_SIZE)
                data_offset += loader_entry_struct[23]
                loader_entry_buf = struct.pack(RK_LOADER_ENTRY_FORMAT, *loader_entry_struct)
                fout.write(loader_entry_buf)

            loader_entry_struct[1] = ENTRYLOADER
            for i in range(count_loader):
                item_name = in_loader_entry[i]
                if not os.path.exists(item_name):
                    print("%s is not existed" % item_name)
                    fout.close()
                    return
                item_size = os.path.getsize(item_name)
                item_name = entry_loader_name[i]
                for j in range(20):
                    if j < len(item_name):
                        loader_entry_struct[2 + j] = ord(item_name[j])
                    else:
                        loader_entry_struct[2 + j] = 0
                loader_entry_struct[22] = data_offset
                loader_entry_struct[23] = align(item_size, PAGE_SIZE)
                data_offset += loader_entry_struct[23]
                loader_entry_buf = struct.pack(RK_LOADER_ENTRY_FORMAT, *loader_entry_struct)
                fout.write(loader_entry_buf)
            #3.write entry data
            for i in range(count_471):
                item_name = in_entry471[i]
                if not input_from_ini:
                    print("writing %s" % item_name)
                file_size = os.path.getsize(item_name)
                item_size = align(file_size,PAGE_SIZE)
                fin = open(item_name, 'rb')
                data_buf = bytearray(fin.read())
                fin.close()
                data_buf = data_buf.ljust(item_size, b'\0')
                if not in_471_rc4:
                    data_buf = rc4(bytes(data_buf))
                fout.write(data_buf)
            for i in range(count_472):
                item_name = in_entry472[i]
                if not input_from_ini:
                    print("writing %s" % item_name)
                file_size = os.path.getsize(item_name)
                item_size = align(file_size,PAGE_SIZE)
                fin = open(item_name, 'rb')
                data_buf = bytearray(fin.read())
                fin.close()
                data_buf = data_buf.ljust(item_size, b'\0')
                if not in_471_rc4:
                    data_buf = rc4(bytes(data_buf))
                fout.write(data_buf)
            for i in range(count_loader):
                item_name = in_loader_entry[i]
                if not input_from_ini:
                    print("writing %s" % item_name)
                file_size = os.path.getsize(item_name)
                item_size = align(file_size, PAGE_SIZE)
                fin = open(item_name, 'rb')
                data_buf = bytearray(fin.read())
                fin.close()
                data_buf = data_buf.ljust(item_size, b'\0')
                for i in range(item_size//SECTOR_SIZE):
                    data_buf[i*SECTOR_SIZE:(i+1)*SECTOR_SIZE] = rc4(bytes(data_buf[i*SECTOR_SIZE:(i+1)*SECTOR_SIZE]))
                fout.write(data_buf)
            #calculate crc
            if not input_from_ini:
                print("writing crc...")
            fout.seek(0, io.SEEK_SET)
            new_loader_data = fout.read()
            crc = crc32(new_loader_data, 0)
            fout.write(crc.to_bytes(4,'little'))
            fout.close()
            print("pack loader ok.(%s)(%.2f)" % (os.path.basename(in_output),timer()-total_start))
        elif cmd.lower() == "unpack":
            parser = argparse.ArgumentParser(description='unpack rk loader', prog='boot_merger unpack')
            parser.add_argument('--version', action='version', version=APP_VERSION)
            parser.add_argument('--loader', nargs=1, help='rk loader to extract')
            parser.add_argument('--output', nargs=1, help='output directory')
            args = parser.parse_args(sys.argv[2:])

            print("unpacking loader start...")
            os_string = platform.system()
            input_loader = args.loader[0]
            output_dir = args.output[0]
            if not os.path.exists(input_loader):
                print("%s is not existed" % input_loader)
                return
            if not os.path.exists(output_dir):
                print("%s is not existed" % output_dir)
                return
            if os_string.lower() == "windows":
                if output_dir[-1] != '\\':
                    output_dir = '%s%s' % (output_dir, '\\')
            else:
                if output_dir[-1] != '/':
                    output_dir = '%s%s' % (output_dir, '/')
            print("loader=%s" % input_loader)
            print("output=%s" % output_dir)
            loader_size = os.path.getsize(input_loader)
            fin = open(input_loader, 'rb')
            loader_data = bytearray(fin.read())
            tag = int.from_bytes(loader_data[0:4], 'little')
            if (tag != BOOT_TAG) and (tag !=LDR_TAG):
                print("loader tag is invalid")
                fin.close()
                return
            ver = int.from_bytes(loader_data[10:14], 'little')
            if tag == LDR_TAG:
                if ver > LDR_FORMAT_VER:
                    print("tool did not support this loader,please upgrade")
                    fin.close()
                    return
            crc = int.from_bytes(loader_data[-4:], 'little')
            new_crc = crc32(bytes(loader_data[:-4]), 0)
            if crc != new_crc:
                print("checking crc failed,crc=0x%08x,new=0x%08x" % (crc,new_crc))
                fin.close()
                return
            head_size = struct.calcsize(RK_LOADER_HEAD_FORMAT)
            entry_size = struct.calcsize(RK_LOADER_ENTRY_FORMAT)
            head_struct = list(struct.unpack(RK_LOADER_HEAD_FORMAT,loader_data[0:head_size]))
            #1.unpack 471
            count_471 = head_struct[6]
            offset_471 = head_struct[7]
            for i in range(count_471):
                entry_struct = list(struct.unpack(RK_LOADER_ENTRY_FORMAT,loader_data[offset_471:offset_471+entry_size]))
                item_name = []
                for j in range(20):
                    if entry_struct[2+j] == 0:
                        break
                    item_name.append(chr(entry_struct[2+j]))
                file_name = ''.join(item_name)
                print("unpacking %s..." % file_name)
                file_name = output_dir + file_name + '.bin'
                data_offset = entry_struct[22]
                data_size = entry_struct[23]
                out_data = bytearray(loader_data[data_offset:data_offset+data_size])
                if not head_struct[17]:
                    out_data = rc4(bytes(out_data))
                fout = open(file_name,'wb')
                fout.write(out_data)
                fout.close()
                offset_471 += entry_size
            # 2.unpack 472
            count_472 = head_struct[9]
            offset_472 = head_struct[10]
            for i in range(count_472):
                entry_struct = list(struct.unpack(RK_LOADER_ENTRY_FORMAT, loader_data[offset_472:offset_472+entry_size]))
                item_name = []
                for j in range(20):
                    if entry_struct[2 + j] == 0:
                        break
                    item_name.append(chr(entry_struct[2 + j]))
                file_name = ''.join(item_name)
                print("unpacking %s..." % file_name)
                file_name = output_dir + file_name + '.bin'
                data_offset = entry_struct[22]
                data_size = entry_struct[23]
                out_data = bytearray(loader_data[data_offset:data_offset + data_size])
                if not head_struct[17]:
                    out_data = rc4(bytes(out_data))
                fout = open(file_name, 'wb')
                fout.write(out_data)
                fout.close()
                offset_472 += entry_size
            # 2.unpack loader
            count_loader = head_struct[12]
            offset_loader = head_struct[13]
            for i in range(count_loader):
                entry_struct = list(struct.unpack(RK_LOADER_ENTRY_FORMAT, loader_data[offset_loader:offset_loader+entry_size]))
                item_name = []
                for j in range(20):
                    if entry_struct[2 + j] == 0:
                        break
                    item_name.append(chr(entry_struct[2 + j]))
                file_name = ''.join(item_name)
                print("unpacking %s..." % file_name)
                file_name = output_dir + file_name + '.bin'
                data_offset = entry_struct[22]
                data_size = entry_struct[23]
                out_data = bytearray(loader_data[data_offset:data_offset + data_size])
                for i in range(data_size//SECTOR_SIZE):
                    out_data[i * SECTOR_SIZE:(i + 1) * SECTOR_SIZE] = rc4(bytes(out_data[i * SECTOR_SIZE:(i + 1) * SECTOR_SIZE]))

                fout = open(file_name, 'wb')
                fout.write(out_data)
                fout.close()
                offset_loader += entry_size

            fin.close()
            print("unpack loader ok.")
        elif cmd.lower() == "change_ver":
            parser = argparse.ArgumentParser(description='change loader version', prog='boot_merger change_ver')
            parser.add_argument('--loader', nargs=1, help='rk loader to change')
            parser.add_argument('--loader_ver', nargs=1, help='version like as xx.xx')
            args = parser.parse_args(sys.argv[2:])

            print("changing loader version start...")
            os_string = platform.system()
            input_loader = args.loader[0]
            in_verion_str = args.loader_ver[0]
            if not os.path.exists(input_loader):
                print("%s is not existed" % input_loader)
                return
            loader_ver = convert_loader_ver(in_verion_str)
            if loader_ver == -1:
                print("invalid loader ver %s" % in_verion_str)
                return
            print("loader=%s" % input_loader)
            print("ver=%s" % in_verion_str)
            loader_size = os.path.getsize(input_loader)
            with open(input_loader, 'rb+') as fin:
                loader_data = bytearray(fin.read())
                tag = int.from_bytes(loader_data[0:4], 'little')
                if (tag != BOOT_TAG) and (tag !=LDR_TAG):
                    print("loader tag is invalid")
                    return
                ver = int.from_bytes(loader_data[10:14], 'little')
                if tag == LDR_TAG:
                    if ver > LDR_FORMAT_VER:
                        print("tool did not support this loader,please upgrade")
                        return
                crc = int.from_bytes(loader_data[-4:], 'little')
                new_crc = crc32(loader_data[:-4], 0)
                if crc != new_crc:
                    print("checking crc failed,crc=0x%08x,new=0x%08x" % (crc, new_crc))
                    fin.close()
                    return
                head_size = struct.calcsize(RK_LOADER_HEAD_FORMAT)
                head_struct = list(struct.unpack(RK_LOADER_HEAD_FORMAT, loader_data[0:head_size]))
                print("old_ver=%x.%x,new_ver=%s" % (head_struct[2]>> 8 & 0xff, head_struct[2] & 0xff, in_verion_str))
                head_struct[2] = loader_ver
                loader_data[0:head_size] = struct.pack(RK_LOADER_HEAD_FORMAT, *head_struct)
                fin.seek(0, io.SEEK_SET)
                fin.write(loader_data[0:head_size])
                fin.seek(-4, io.SEEK_END)
                crc = crc32(loader_data[:-4], 0)
                fin.write(crc.to_bytes(4,'little'))
                print("change version of loader ok.")
        elif cmd.lower() == "ins_cert":
            parser = argparse.ArgumentParser(description='insert cert into rkloader', prog='boot_merger ins_cert')
            parser.add_argument('--loader', nargs=1, help='rkloader')
            parser.add_argument('--cert', nargs=1, help='CA cert')
            args = parser.parse_args(sys.argv[2:])

            print("insert cert into loader start...")
            input_loader = args.loader[0]
            cert_file = args.cert[0]
            if not os.path.exists(input_loader):
                print("%s is not existed" % input_loader)
                return
            if not os.path.exists(cert_file):
                print("%s is not existed" % cert_file)
                return

            print("loader=%s" % input_loader)
            print("cert=%s" % cert_file)
            loader_size = os.path.getsize(input_loader)
            with open(input_loader,'rb+') as fin,open(cert_file,'rb') as fcert:
                loader_data = bytearray(fin.read())
                tag = int.from_bytes(loader_data[0:4], 'little')
                if (tag != BOOT_TAG) and (tag !=LDR_TAG):
                    print("loader tag is invalid")
                    return
                ver = int.from_bytes(loader_data[10:14], 'little')
                if tag == LDR_TAG:
                    if ver > LDR_FORMAT_VER:
                        print("tool did not support this loader,please upgrade")
                        return
                cert_data = bytearray(fcert.read())
                if cert_data[0:4].decode() != 'RKPK':
                    print('cert tag is invalid')
                    return
                if len(cert_data) != 2048:
                    print('size of cet is not 2048B')
                    return
                for i in range(4):
                    cert_data[i * SECTOR_SIZE:(i + 1) * SECTOR_SIZE] = rc4(bytes(cert_data[i * SECTOR_SIZE:(i + 1) * SECTOR_SIZE]))
                crc = int.from_bytes(loader_data[-4:], 'little')
                new_crc = crc32(loader_data[:-4], 0)
                if crc != new_crc:
                    print("checking crc failed,crc=0x%08x,new=0x%08x" % (crc,new_crc))
                    return
                head_size = struct.calcsize(RK_LOADER_HEAD_FORMAT)
                entry_size = struct.calcsize(RK_LOADER_ENTRY_FORMAT)
                head_struct = list(struct.unpack(RK_LOADER_HEAD_FORMAT,loader_data[0:head_size]))

                # modify loader entry
                count_loader = head_struct[12]
                offset_loader = head_struct[13]
                flashhead_offset = 0
                new_flashhead_data = bytearray(4096)
                for i in range(count_loader):
                    entry_struct = list(struct.unpack(RK_LOADER_ENTRY_FORMAT, loader_data[offset_loader:offset_loader+entry_size]))
                    item_name = []
                    for j in range(20):
                        if entry_struct[2 + j] == 0:
                            break
                        item_name.append(chr(entry_struct[2 + j]))
                    file_name = ''.join(item_name)
                    if file_name.lower()=='flashhead':
                        flashhead_offset = entry_struct[22]
                        flashhead_size = entry_struct[23]
                        new_flashhead_data[0:2048] = loader_data[flashhead_offset:flashhead_offset + 2048]
                        new_flashhead_data[2048:] = cert_data

                        if flashhead_size == 4096:
                            break
                        else:
                            entry_struct[23] = 4096
                    else:
                        if flashhead_offset != 0:
                            entry_struct[22] += 2048
                    if flashhead_offset != 0:
                        loader_data[offset_loader:offset_loader + entry_size] = struct.pack(RK_LOADER_ENTRY_FORMAT,*entry_struct)
                    offset_loader += entry_size
                if flashhead_offset == 0:
                    print('no found flashhead entry in the loader')
                    return
                if flashhead_size == 4096:
                    new_loader_data = bytearray(loader_size)
                else:
                    new_loader_data = bytearray(loader_size+2048)
                new_loader_data[0:flashhead_offset] = loader_data[0:flashhead_offset]
                new_loader_data[flashhead_offset:flashhead_offset+4096] = new_flashhead_data
                new_loader_data[flashhead_offset+4096:-4] = loader_data[flashhead_offset+flashhead_size:-4]
                fin.seek(0,os.SEEK_SET)
                fin.truncate(0)
                fin.write(new_loader_data[:-4])
                crc = crc32(new_loader_data[:-4], 0)
                fin.write(crc.to_bytes(4,'little'))

            print("insert cert  ok.")
        elif cmd.lower() == "del_cert":
            parser = argparse.ArgumentParser(description='delete cert from rkloader', prog='boot_merger del_cert')
            parser.add_argument('--loader', nargs=1, help='rkloader')
            args = parser.parse_args(sys.argv[2:])

            print("delete cert from loader start...")
            input_loader = args.loader[0]
            if not os.path.exists(input_loader):
                print("%s is not existed" % input_loader)
                return

            print("loader=%s" % input_loader)
            loader_size = os.path.getsize(input_loader)
            with open(input_loader,'rb+') as fin:
                loader_data = bytearray(fin.read())
                tag = int.from_bytes(loader_data[0:4], 'little')
                if (tag != BOOT_TAG) and (tag !=LDR_TAG):
                    print("loader tag is invalid")
                    return
                ver = int.from_bytes(loader_data[10:14], 'little')
                if tag == LDR_TAG:
                    if ver > LDR_FORMAT_VER:
                        print("tool did not support this loader,please upgrade")
                        return
                crc = int.from_bytes(loader_data[-4:], 'little')
                new_crc = crc32(loader_data[:-4], 0)
                if crc != new_crc:
                    print("checking crc failed,crc=0x%08x,new=0x%08x" % (crc,new_crc))
                    return
                head_size = struct.calcsize(RK_LOADER_HEAD_FORMAT)
                entry_size = struct.calcsize(RK_LOADER_ENTRY_FORMAT)
                head_struct = list(struct.unpack(RK_LOADER_HEAD_FORMAT,loader_data[0:head_size]))

                # modify loader entry
                count_loader = head_struct[12]
                offset_loader = head_struct[13]
                flashhead_offset = 0
                new_flashhead_data = bytearray(2048)
                for i in range(count_loader):
                    entry_struct = list(struct.unpack(RK_LOADER_ENTRY_FORMAT, loader_data[offset_loader:offset_loader+entry_size]))
                    item_name = []
                    for j in range(20):
                        if entry_struct[2 + j] == 0:
                            break
                        item_name.append(chr(entry_struct[2 + j]))
                    file_name = ''.join(item_name)
                    if file_name.lower()=='flashhead':
                        flashhead_offset = entry_struct[22]
                        flashhead_size = entry_struct[23]
                        if flashhead_size != 2048 and flashhead_size != 4096:
                            print('size of flashhead is invalid')
                            return
                        new_flashhead_data[0:2048] = loader_data[flashhead_offset:flashhead_offset + 2048]
                        if flashhead_size == 2048:
                            break
                        else:
                            entry_struct[23] = 2048
                    else:
                        if flashhead_offset != 0:
                            entry_struct[22] -= 2048
                    if flashhead_offset != 0:
                        loader_data[offset_loader:offset_loader + entry_size] = struct.pack(RK_LOADER_ENTRY_FORMAT,*entry_struct)
                    offset_loader += entry_size
                if flashhead_offset == 0:
                    print('no found flashhead entry in the loader')
                    return
                if flashhead_size == 4096:
                    new_loader_data = bytearray(loader_size-2048)
                    new_loader_data[0:flashhead_offset] = loader_data[0:flashhead_offset]
                    new_loader_data[flashhead_offset:flashhead_offset+2048] = new_flashhead_data
                    new_loader_data[flashhead_offset+2048:-4] = loader_data[flashhead_offset+flashhead_size:-4]
                    fin.seek(0,os.SEEK_SET)
                    fin.truncate(0)
                    fin.write(new_loader_data[:-4])
                    crc = crc32(new_loader_data[:-4], 0)
                    fin.write(crc.to_bytes(4,'little'))

            print("delete cert  ok.")
        else:
            print("invalid %s command" % (cmd))
            usage()
    else:
        usage()

if __name__ == '__main__':
    boot_merger_main()