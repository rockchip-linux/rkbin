#!/bin/bash
#
# Copyright (c) 2024 Rockchip Electronics Co., Ltd
#
# SPDX-License-Identifier: GPL-2.0
#
set -e

SIGN_DIR=".fit_sign"
SIGN_OUTPUT="${SIGN_DIR}/output"
UNPACK_UBOOT="${SIGN_DIR}/unpack_uboot"
UNPACK_LOADER="${SIGN_DIR}/unpack_loader"
TOOLS=$(cd `dirname $0`; pwd)
# tools
TOOL_MKIMAGE=${TOOLS}/mkimage
TOOL_FIT_UNPACK=${TOOLS}/fit-unpack.sh
TOOL_FIT_CHECK_SIGN=${TOOLS}/fit_check_sign
TOOL_RK_SIGN=${TOOLS}/rk_sign_tool
TOOL_BOOT_MERGER=${TOOLS}/boot_merger
# offset
OFFS_DATA=0x1200
# placeholder address
FDT_ADDR_PLACEHOLDER="0xffffff00"
KERNEL_ADDR_PLACEHOLDER="0xffffff01"
RAMDISK_ADDR_PLACEHOLDER="0xffffff02"
# key
SIGNATURE_KEY_NODE="/signature/key-dev"
# dtb
SPL_DTB="${UNPACK_LOADER}/u-boot-spl.dtb"
UBOOT_DTB="${UNPACK_UBOOT}/fdt"
UBOOT_DTB_ORIG="${UNPACK_UBOOT}/fdt_orig"
# uboot
ITS_UBOOT="${UNPACK_UBOOT}/image.its"
ITB_UBOOT="${UNPACK_UBOOT}/image.itb"
IMG_UBOOT="${SIGN_OUTPUT}/uboot.img"
# rollback & version
declare -A ROLLBACK_PARAMS
declare -A VERSION_PARAMS

# All required tools:
#
#    ├── boot_merger
#    ├── fit_check_sign
#    ├── fit-unpack.sh
#    ├── mkimage
#    ├── rk_sign_tool
#    └── setting.ini

function filt_val()
{
	sed -n "/${1}=/s/${1}=//p" $2 | tr -d '\r' | tr -d '"'
}

function help()
{
	echo
	echo "Usage:"
	echo "    $0 [args]"
	echo
	echo "Args:"
	echo "    --key-dir                  <dir>                         | Mandatory"
	echo "    --src-dir                  <dir>                         | Mandatory"
	echo "    --out-dir                  <dir>                         | Mandatory"
	echo "    --burn-key-hash                                          | Optional"
	echo "    --rollback-index           <image1 n1> <image2 n2> ...   | Optional"
	echo "    --version                  <image1 n1> <image2 n2> ...   | Optional"
	echo ""
	echo "Example:"
	echo "    $0 --key-dir keys/ --src-dir src/ --out-dir output/  --version uboot.img 1 boot.img 3  --rollback-index uboot.img 3 boot.img 5"
	echo
}

function arg_check_decimal()
{
	if [ -z $1 ]; then
		help
		exit 1
	fi

	DECIMAL=`echo $1 |sed 's/[0-9]//g'`
	if [ ! -z ${DECIMAL} ]; then
		echo "ERROR: $1 is not decimal integer"
		help
		exit 1
	fi
}

function process_args()
{
	while [ $# -gt 0 ]; do
		case $1 in
			--key-dir)
				ARG_KEY_DIR=$2
				RSA_PRI_KEY="${ARG_KEY_DIR}/dev.key"
				RSA_PUB_KEY="${ARG_KEY_DIR}/dev.pubkey"
				RSA_CRT_KEY="${ARG_KEY_DIR}/dev.crt"
				check_dir_exist $2
				check_rsa_keys $2
				shift 2
				;;
			--src-dir)
				ARG_SRC_DIR=$2
				check_dir_exist $2
				SIGN_CFG_DIR="${ARG_SRC_DIR}/fit_signcfg/"
				SIGN_CONFIG="${ARG_SRC_DIR}/fit_signcfg/sign.readonly_config"
				shift 2
				;;
			--out-dir)
				ARG_OUTPUT_DIR=$2
				check_dir_exist $2
				shift 2
				;;
			--rollback-index)
				shift 1
				for arg in "$@"; do
					FILE_NAME="${1%.img}"
					arg_check_decimal $2
					ROLLBACK_PARAMS["${FILE_NAME}"]="$2"
					if [[ $3 == *"--"* || -z $3 ]]; then
						shift 2
						break;
					fi
					shift 2
				done
				;;
			--version)
				shift 1
				for arg in "$@"; do
					FILE_NAME="${1%.img}"
					arg_check_decimal $2
					VERSION_PARAMS["${FILE_NAME}"]="$2"
					if [[ $3 == *"--"* || -z $3 ]]; then
						shift 2
						break;
					fi
					shift 2
				done
				;;
			--burn-key-hash)
				ARG_BURN_KEY_HASH="y"
				shift 1
				;;
			*)
				help
				exit 1
				;;
		esac
	done

	if [ -z "${ARG_KEY_DIR}" ] || [ -z "${ARG_SRC_DIR}" ] || [ -z "${ARG_OUTPUT_DIR}" ]; then
		help
		exit 1
	fi
}

function check_dir_exist()
{
	if [ ! -d $1 ]; then
		echo "ERROR: No $1 directory"
		exit 1
	fi
}

function check_file_exist()
{
	if [ ! -f $1 ]; then
		echo "ERROR: No $1"
		exit 1
	fi
}

function check_its()
{
	cat $1 | while read LINE
	do
		FILE=`echo ${LINE} | sed -n "/incbin/p" | awk -F '"' '{ printf $2 }' | tr -d ' '`
		if [ ! -f ${FILE} ]; then
			echo "ERROR: ${FILE} not exist"
			exit 1
		fi
	done
}

function check_rsa_algo()
{
	if grep -q '^CONFIG_FIT_ENABLE_RSA4096_SUPPORT=y' ${SIGN_CONFIG} ; then
		RSA_ALGO="rsa4096"
	else
		RSA_ALGO="rsa2048"
	fi

	if ! grep -q ${RSA_ALGO} $1 ; then
		echo "ERROR: Wrong rsa 'algo' in its file. It should be ${RSA_ALGO}."
		exit 1
	fi
}

function check_rsa_keys()
{
	if [ ! -f ${RSA_PRI_KEY} ]; then
		echo "ERROR: No ${RSA_PRI_KEY} "
		exit 1
	elif [ ! -f ${RSA_PUB_KEY} ]; then
		echo "ERROR: No ${RSA_PUB_KEY} "
		exit 1
	elif [ ! -f ${RSA_CRT_KEY} ]; then
		echo "ERROR: No ${RSA_CRT_KEY} "
		exit 1
	fi
}

function sign_loader()
{
	echo
	echo "==================== sign loader ===================="
	cp ${INI_PATH} ${UNPACK_LOADER}/
	INI_PATH=`find ${UNPACK_LOADER}/ -name 'MINIALL.ini'`
	sed -i "s|PATH=|PATH=${SIGN_OUTPUT}\/|g" ${INI_PATH}

	# code471
	DDR=`grep "Path1=bin/[^ ]*_ddr_" ${INI_PATH} | tr -d ' '`
	if [ ! -z ${DDR} ]; then
		DDR=${DDR/*=/}
		NEW_DDR=`find ${UNPACK_LOADER}/ -name '*ddr*bin' | head -n 1`
		echo "${DDR} ${NEW_DDR}"
		sed -i "s|${DDR}|${NEW_DDR}|g" ${INI_PATH}
	fi
	# code472
	USBPLUG=`grep "Path1=bin/[^ ]*_usbplug_" ${INI_PATH} | tr -d ' '`
	if [ ! -z ${USBPLUG} ]; then
		USBPLUG=${USBPLUG/*=/}
		NEW_USBPLUG=`find ${UNPACK_LOADER}/ -name '*usbplug*bin' | head -n 1`
		echo "${USBPLUG} ${NEW_USBPLUG}"
		sed -i "s|${USBPLUG}|${NEW_USBPLUG}|g" ${INI_PATH}
	fi
	# FlashData
	FlashData=`grep "FlashData=bin/[^ ]*_ddr_" ${INI_PATH} | tr -d ' '`
	if [ ! -z ${FlashData} ]; then
		FlashData=${FlashData/*=/}
		NEW_FlashData=`find ${UNPACK_LOADER}/ -name '*FlashData*bin' | head -n 1`
		echo "${FlashData} ${NEW_FlashData}"
		sed -i "s|${FlashData}|${NEW_FlashData}|g" ${INI_PATH}
	fi
	# FlashBoot
	FlashBoot=`grep "FlashBoot=bin/[^ ]*_spl_" ${INI_PATH} | tr -d ' '`
	if [ ! -z ${FlashBoot} ]; then
		FlashBoot=${FlashBoot/*=/}
		NEW_FlashBoot=`find ${UNPACK_LOADER}/ -name '*FlashBoot*bin' | head -n 1`
		echo "${FlashBoot} ${NEW_FlashBoot}"
		sed -i "s|${FlashBoot}|${NEW_FlashBoot}|g" ${INI_PATH}
	fi
	# FlashBoost
	FlashBoost=`grep "FlashBoost=bin/[^ ]*_boost_" ${INI_PATH} | tr -d ' '`
	if [ ! -z ${FlashBoost} ]; then
		FlashBoost=${FlashBoost/*=/}
		NEW_FlashBoot=`find ${UNPACK_LOADER}/ -name '*FlashBoost*bin' | head -n 1`
		echo "${FlashBoost} ${NEW_FlashBoot}"
		sed -i "s|${FlashBoost}|${NEW_FlashBoot}|g" ${INI_PATH}
	fi

	${TOOL_BOOT_MERGER} ${INI_PATH}

	# chip name
	CHIP_PATTERN='^CONFIG_ROCKCHIP_[R,P][X,V,K][0-9ESXB]{1,5}'
	RKCHIP=`egrep -o ${CHIP_PATTERN} ${SIGN_CONFIG}`
	RKCHIP=${RKCHIP##*_}
	CHIP_NAME=`filt_val "CONFIG_CHIP_NAME" ${SIGN_CONFIG}`
	if [ -z "${CHIP_NAME}" ]; then
		CHIP_NAME=${RKCHIP}
	fi

	# sign
	${TOOL_RK_SIGN} cc --chip ${CHIP_NAME: 2: 6}
	${TOOL_RK_SIGN} lk --key ${RSA_PRI_KEY} --pubkey ${RSA_PUB_KEY}
	if ls ${SIGN_OUTPUT}/*loader*.bin >/dev/null 2>&1 ; then
		${TOOL_RK_SIGN} sl --loader ${SIGN_OUTPUT}/*loader*.bin
	fi
	if ls ${SIGN_OUTPUT}/*download*.bin >/dev/null 2>&1 ; then
		${TOOL_RK_SIGN} sl --loader ${SIGN_OUTPUT}/*download*.bin
	fi
	if ls ${SIGN_OUTPUT}/*idblock*.img >/dev/null 2>&1 ; then
		${TOOL_RK_SIGN} sb --idb ${SIGN_OUTPUT}/*idblock*.img
	fi
}

function sign_uboot()
{
	ARG_ROLLBACK_IDX_UBOOT=${ROLLBACK_PARAMS["uboot"]:-0}
	ARG_VER_UBOOT=${VERSION_PARAMS["uboot"]:-0}

	echo
	echo "==================== sign uboot.img: version=${ARG_VER_UBOOT}, rollback-index=${ARG_ROLLBACK_IDX_UBOOT} ===================="
	if ! grep -q '^CONFIG_SPL_FIT_SIGNATURE=y' ${SIGN_CONFIG} ; then
		echo "ERROR: CONFIG_SPL_FIT_SIGNATURE is disabled"
		exit 1
	fi
	# spl dtb
	FlashBoot=`find ${UNPACK_LOADER}/ -name '*FlashBoot*bin' | head -n 1`
	TOTALSIZE=`fdtdump -s ${FlashBoot} | grep totalsize | awk '{ print $4 }' | tr -d "()"`
	OFFSET=`fdtdump -s ${FlashBoot} | head -1 | awk -F ":" '{ print $2 }' | sed "s/ found fdt at offset //g" | tr -d " "`
	if [ -z ${OFFSET}  ]; then
		echo "ERROR: invalid ${FlashBoot} , unable to find fdt blob"
	fi
	OFFSET=`printf %d ${OFFSET} ` # hex -> dec

	dd if=${FlashBoot} of=${SPL_DTB} bs=1 skip=${OFFSET} count=${TOTALSIZE} >/dev/null 2>&1

	# rollback-index
	if grep -q '^CONFIG_SPL_FIT_ROLLBACK_PROTECT=y' ${SIGN_CONFIG} ; then
		ARG_SPL_ROLLBACK_PROTECT="y"
		if [ ${ARG_ROLLBACK_IDX_UBOOT} -eq 0 ]; then
			echo "ERROR: No arg \"--rollback-index uboot.img <n>\""
			exit 1
		fi
	fi

	if [ "${ARG_SPL_ROLLBACK_PROTECT}" == "y" ]; then
		VERSION=`grep 'rollback-index' ${ITS_UBOOT} | awk -F '=' '{ printf $2 }' | tr -d ' '`
		sed -i "s/rollback-index = ${VERSION}/rollback-index = <${ARG_ROLLBACK_IDX_UBOOT}>;/g" ${ITS_UBOOT}
	fi

	if ! fdtget -l ${UBOOT_DTB} /signature >/dev/null 2>&1 ; then
		${TOOL_MKIMAGE} -f ${ITS_UBOOT} -k ${ARG_KEY_DIR} -K ${UBOOT_DTB} -E -p ${OFFS_DATA} -r ${ITB_UBOOT} -v ${ARG_VER_UBOOT}
		echo "## Adding RSA public key into ${UBOOT_DTB}"
	fi

	if fdtget -l ${SPL_DTB} /signature >/dev/null 2>&1 ; then
		fdtput -r ${SPL_DTB} /signature
	fi

	# sign
	${TOOL_MKIMAGE} -f ${ITS_UBOOT} -k ${ARG_KEY_DIR} -K ${SPL_DTB} -E -p ${OFFS_DATA} -r ${ITB_UBOOT} -v ${ARG_VER_UBOOT}

	# burn-key-hash
	if [ "${ARG_BURN_KEY_HASH}" == "y" ]; then
		if grep -q '^CONFIG_SPL_FIT_HW_CRYPTO=y' ${SIGN_CONFIG} ; then
			fdtput -tx ${SPL_DTB} ${SIGNATURE_KEY_NODE} burn-key-hash 0x1
		else
			echo "ERROR: --burn-key-hash requires CONFIG_SPL_FIT_HW_CRYPTO=y"
			exit 1
		fi
	fi

	# rollback-index read back check
	if [ "${ARG_SPL_ROLLBACK_PROTECT}" == "y" ]; then
		VERSION=`fdtget -ti ${ITB_UBOOT} /configurations/conf rollback-index`
		if [ "${VERSION}" != "${ARG_ROLLBACK_IDX_UBOOT}" ]; then
			echo "ERROR: Failed to set rollback-index for ${ITB_UBOOT}";
			exit 1
		fi
	else
		if [ ! -z "${ARG_ROLLBACK_IDX_UBOOT}" ]; then
			echo "WARNING: ignore \"--rollback-index uboot.img ${ARG_ROLLBACK_IDX_UBOOT}\" due to CONFIG_SPL_FIT_ROLLBACK_PROTECT=n"
			echo
		fi
	fi

	# burn-key-hash read back check
	if [ "${ARG_BURN_KEY_HASH}" == "y" ]; then
		if [ "`fdtget -ti ${SPL_DTB} ${SIGNATURE_KEY_NODE} burn-key-hash`" != "1" ]; then
			echo "ERROR: Failed to set burn-key-hash for ${SPL_DTB}";
			exit 1
		fi
	fi

	# host check signature
	${TOOL_FIT_CHECK_SIGN} -f ${ITB_UBOOT} -k ${SPL_DTB} -s

	# minimize u-boot-spl.dtb: clear as 0 but not remove property.
	if grep -q '^CONFIG_SPL_FIT_HW_CRYPTO=y' ${SIGN_CONFIG} ; then
		fdtput -tx ${SPL_DTB} ${SIGNATURE_KEY_NODE} rsa,r-squared 0x0
		if grep -q '^CONFIG_SPL_ROCKCHIP_CRYPTO_V1=y' ${SIGN_CONFIG} ; then
			fdtput -tx ${SPL_DTB} ${SIGNATURE_KEY_NODE} rsa,np 0x0
			fdtput -r ${SPL_DTB} ${SIGNATURE_KEY_NODE}/hash@np
		else
			fdtput -tx ${SPL_DTB} ${SIGNATURE_KEY_NODE} rsa,c 0x0
			fdtput -r ${SPL_DTB} ${SIGNATURE_KEY_NODE}/hash@c
		fi
	else
		fdtput -tx ${SPL_DTB} ${SIGNATURE_KEY_NODE} rsa,c 0x0
		fdtput -tx ${SPL_DTB} ${SIGNATURE_KEY_NODE} rsa,np 0x0
		fdtput -tx ${SPL_DTB} ${SIGNATURE_KEY_NODE} rsa,exponent-BN 0x0
		fdtput -r ${SPL_DTB} ${SIGNATURE_KEY_NODE}/hash@c
		fdtput -r ${SPL_DTB} ${SIGNATURE_KEY_NODE}/hash@np
	fi

	# repack spl
	dd if=${SPL_DTB} of=${FlashBoot} bs=${OFFSET} seek=1 >/dev/null 2>&1

	if [ "${ARG_BURN_KEY_HASH}" == "y" ]; then
		echo "## ${SPL_DTB}: burn-key-hash=1"
	fi

	ITB_MAX_NUM=`sed -n "/CONFIG_SPL_FIT_IMAGE_MULTIPLE/p" ${SIGN_CONFIG} | awk -F "=" '{ print $2 }'`
	ITB_MAX_KB=`sed  -n "/CONFIG_SPL_FIT_IMAGE_KB/p" ${SIGN_CONFIG} | awk -F "=" '{ print $2 }'`
	ITB_MAX_BS=$((ITB_MAX_KB*1024))
	ITB_BS=`ls -l ${ITB_UBOOT} | awk '{ print $5 }'`

	if [ ${ITB_BS} -gt ${ITB_MAX_BS} ]; then
		echo "ERROR: pack uboot.img failed! ${ITB_UBOOT} actual: ${ITB_BS} bytes, max limit: ${ITB_MAX_BS} bytes"
		exit 1
	fi

	for ((i = 0; i < ${ITB_MAX_NUM}; i++));
	do
		cat ${ITB_UBOOT} >> ${IMG_UBOOT}
		truncate -s %${ITB_MAX_KB}K ${IMG_UBOOT}
	done
}

function sign_fit()
{
	SRC_FILE="$1.img"
	UNPACK_DIR="${SIGN_DIR}/unpack_$1"
	ITS_FILE="${UNPACK_DIR}/image.its"
	ITB_FILE="${UNPACK_DIR}/image.itb"
	IMG_FILE="${SIGN_OUTPUT}/${SRC_FILE}"
	ARG_VERSION=${VERSION_PARAMS["$1"]:-0}
	ARG_ROLLBACK_IDX=${ROLLBACK_PARAMS["$1"]:-0}

	echo
	echo "==================== sign ${SRC_FILE}: version=${ARG_VERSION}, rollback-index=${ARG_ROLLBACK_IDX} ===================="
	cp ${UBOOT_DTB_ORIG} ${UBOOT_DTB}
	rm -rf ${UNPACK_DIR}
	${TOOL_FIT_UNPACK} -f ${ARG_SRC_DIR}/${SRC_FILE} -o ${UNPACK_DIR}
	check_rsa_algo ${ITS_FILE}

	if ! grep -q '^CONFIG_FIT_SIGNATURE=y' ${SIGN_CONFIG} ; then
		echo "ERROR: CONFIG_FIT_SIGNATURE is disabled"
		exit 1
	fi

	# ARG_ROLLBACK_IDX default value is 0.
	if grep -q '^CONFIG_FIT_ROLLBACK_PROTECT=y' ${SIGN_CONFIG} ; then
		ARG_ROLLBACK_PROTECT="y"
		if ! grep -q '^CONFIG_OPTEE_CLIENT=y' ${SIGN_CONFIG} ; then
			if [ ${ARG_ROLLBACK_IDX} -gt 0 ]; then
				echo "ERROR: Don't support \"--rollback-index ${SRC_FILE} <n>\" due to CONFIG_FIT_ROLLBACK_PROTECT=y but CONFIG_OPTEE_CLIENT=n"
				exit 1
			fi
		else
			if [ ${ARG_ROLLBACK_IDX} -eq 0 ]; then
				echo "ERROR: No arg \"--rollback-index ${SRC_FILE} <n>\""
				exit 1
			fi
		fi
	else
		if [ ${ARG_ROLLBACK_IDX} -gt 0 ]; then
			echo "WARNING: ignore \"--rollback-index ${SRC_FILE} ${ARG_ROLLBACK_IDX}\" due to CONFIG_FIT_ROLLBACK_PROTECT=n"
			echo
		fi
	fi

	# Limit as same.
	if [ -z "${PREV_ARG_ROLLBACK_IDX}" ]; then
		PREV_ARG_ROLLBACK_IDX=${ARG_ROLLBACK_IDX}
	else
		if [ "${PREV_ARG_ROLLBACK_IDX}" != "${ARG_ROLLBACK_IDX}" ]; then
			echo "ERROR: ${SRC_FILE} rollback version should be the same as previous: ${PREV_ARG_ROLLBACK_IDX}"
			exit 1
		fi
	fi

	# fixup for non-thunderboot
	FDT_ADDR_R=`filt_val "fdt_addr_r" ${SIGN_CONFIG}`
	KERNEL_ADDR_R=`filt_val "kernel_addr_r" ${SIGN_CONFIG}`
	RAMDISK_ADDR_R=`filt_val "ramdisk_addr_r" ${SIGN_CONFIG}`
	sed -i "s/${FDT_ADDR_PLACEHOLDER}/${FDT_ADDR_R}/g"         ${ITS_FILE}
	sed -i "s/${KERNEL_ADDR_PLACEHOLDER}/${KERNEL_ADDR_R}/g"   ${ITS_FILE}
	sed -i "s/${RAMDISK_ADDR_PLACEHOLDER}/${RAMDISK_ADDR_R}/g" ${ITS_FILE}

	if [ "${ARG_ROLLBACK_PROTECT}" == "y" ]; then
		VERSION=`grep 'rollback-index' ${ITS_FILE} | awk -F '=' '{ printf $2 }' | tr -d ' '`
		sed -i "s/rollback-index = ${VERSION}/rollback-index = <${ARG_ROLLBACK_IDX}>;/g" ${ITS_FILE}
	fi

	# sign
	${TOOL_MKIMAGE} -f ${ITS_FILE} -k ${ARG_KEY_DIR} -K ${UBOOT_DTB} -E -p ${OFFS_DATA} -r ${ITB_FILE} -v ${ARG_VERSION}

	# rollback-index read back check
	if [ "${ARG_ROLLBACK_PROTECT}" == "y" ]; then
		VERSION=`fdtget -ti ${ITB_FILE} /configurations/conf rollback-index`
		if [ "${VERSION}" != "${ARG_ROLLBACK_IDX}" ]; then
			echo "ERROR: Failed to set rollback-index for ${ITB_FILE}";
			exit 1
		fi
	fi

	# host check signature
	${TOOL_FIT_CHECK_SIGN} -f ${ITB_FILE} -k ${UBOOT_DTB}

	# minimize u-boot.dtb: clearn as 0 but not remove property.
	if grep -q '^CONFIG_FIT_HW_CRYPTO=y' ${SIGN_CONFIG} ; then
		fdtput -tx ${UBOOT_DTB} ${SIGNATURE_KEY_NODE} rsa,r-squared 0x0
		if grep -q '^CONFIG_ROCKCHIP_CRYPTO_V1=y' ${SIGN_CONFIG} ; then
			fdtput -tx ${UBOOT_DTB} ${SIGNATURE_KEY_NODE} rsa,np 0x0
		else
			fdtput -tx ${UBOOT_DTB} ${SIGNATURE_KEY_NODE} rsa,c 0x0
		fi
	else
		fdtput -tx ${UBOOT_DTB} ${SIGNATURE_KEY_NODE} rsa,c 0x0
		fdtput -tx ${UBOOT_DTB} ${SIGNATURE_KEY_NODE} rsa,np 0x0
		fdtput -tx ${UBOOT_DTB} ${SIGNATURE_KEY_NODE} rsa,exponent-BN 0x0
	fi
	fdtput -r ${UBOOT_DTB} ${SIGNATURE_KEY_NODE}/hash@c
	fdtput -r ${UBOOT_DTB} ${SIGNATURE_KEY_NODE}/hash@np

	cp ${ITB_FILE} ${IMG_FILE}
}

function unpack_loader_uboot()
{
	echo
	echo "==================== unpack files ===================="
	# unpack loader
	rm -rf ${UNPACK_LOADER}/ && mkdir -p ${UNPACK_LOADER}/
	${TOOL_BOOT_MERGER} unpack -i ${LOADER_NAME} -o ${UNPACK_LOADER}/

	# csum spl
	FlashBoot=`find ${UNPACK_LOADER}/ -name '*FlashBoot*bin' | head -n 1`
	SIZE=`grep 'spl_size=' ${SIGN_CONFIG} | awk -F "=" '{print $2}'`
	dd if=${FlashBoot} of=${UNPACK_LOADER}/u-boot-spl-nodtb.bin bs=1 skip=0 count=${SIZE} >/dev/null 2>&1
	CSUM1=`grep 'spl_sha256sum=' ${SIGN_CONFIG} | awk -F "=" '{print $2}'`
	CSUM2=`sha256sum ${UNPACK_LOADER}/u-boot-spl-nodtb.bin | awk '{ print $1 }'`
	if [ "${CSUM1}" != "${CSUM2}" ]; then
		echo "ERROR: SHA256 checksum is not match:"
		echo "    ${CSUM1}: ${LOADER_NAME}/"
		echo "    ${CSUM2}: ${SIGN_CONFIG} history"
		echo
		echo "Build info of ${SIGN_CONFIG}:"
		echo "    ${BUILD}"
		echo
		exit 1
	fi

	# unpack uboot.img
	rm -rf ${UNPACK_UBOOT}/
	${TOOL_FIT_UNPACK} -f ${ARG_SRC_DIR}/uboot.img -o ${UNPACK_UBOOT}

	# csum uboot
	CSUM1=`grep 'uboot_sha256sum=' ${SIGN_CONFIG} | awk -F "=" '{print $2}'`
	CSUM2=`sha256sum ${UNPACK_UBOOT}/uboot | awk '{ print $1 }'`
	BUILD=`grep 'BUILD:' ${SIGN_CONFIG}`
	if [ "${CSUM1}" != "${CSUM2}" ]; then
		echo "ERROR: SHA256 checksum is not match:"
		echo "    ${CSUM1}: uboot in ${ARG_SRC_DIR}/uboot.img"
		echo "    ${CSUM2}: in ${SIGN_CONFIG}"
		echo
		echo "Build info of ${SIGN_CONFIG}:"
		echo "    ${BUILD}"
		echo
		exit 1
	fi

	check_rsa_algo ${ITS_UBOOT}
	if fdtget -l ${UBOOT_DTB} /signature >/dev/null 2>&1 ; then
		fdtput -r ${UBOOT_DTB} /signature
	fi
	cp ${UBOOT_DTB} ${UBOOT_DTB_ORIG}
}

function prepare()
{
	if [ ! -d ${SIGN_CFG_DIR} ]; then
		echo "ERROR: No ${SIGN_CFG_DIR} directory"
		exit 1
	fi
	if [ ! -f ${SIGN_CONFIG} ]; then
		echo "ERROR: No ${SIGN_CONFIG} file"
		exit 1
	fi
	if [ ! -f ${ARG_SRC_DIR}/uboot.img ]; then
		echo "ERROR: No ${ARG_SRC_DIR}/uboot.img file"
		exit 1
	fi
	INI_PATH=`find ${SIGN_CFG_DIR} -name 'MINIALL.ini' | head -n 1`
	if [ -z "${INI_PATH}" ]; then
		echo "ERROR: No platform MINIALL.ini file"
		exit 1
	fi
	LOADER_NAME=`find ${ARG_SRC_DIR} -name '*loader*bin' | head -n 1`
	if [ -z "${LOADER_NAME}" ]; then
		LOADER_NAME=`find ${ARG_SRC_DIR} -name '*download*.bin' | head -n 1`
	fi
	if [ -z "${LOADER_NAME}" ]; then
		echo "ERROR: No platform loader or download found"
		exit 1
	fi

	rm -rf ${SIGN_DIR} && mkdir -p ${SIGN_OUTPUT}
}

function finish()
{
	echo
	echo "Rollback-Index:"
	for FILE in ${SIGN_OUTPUT}/*.img; do
		if file ${FILE} | grep -q 'Device Tree Blob' ; then
			VERSION=`fdtget -ti ${FILE} /configurations/conf rollback-index`
			NAME=`basename ${FILE}`
			echo "    - ${NAME}=${VERSION}"
		fi
	done
	echo
	echo "OK. Signed images are ready in ${ARG_OUTPUT_DIR}:"
	ls ${SIGN_OUTPUT}
	mv ${SIGN_OUTPUT}/* ${ARG_OUTPUT_DIR}/
	rm -rf ${SIGN_DIR}/ data2sign*
	echo
}

function main()
{
	prepare
	unpack_loader_uboot

	for FILE in ${ARG_SRC_DIR}/*.img; do
		if echo ${FILE} | grep -q "uboot.img"; then
			continue;
		fi
		if file ${FILE} | grep -q 'Device Tree Blob' ; then
			FILE=$(basename "${FILE}" .img)
			sign_fit ${FILE}
		fi
	done

	sign_uboot
	sign_loader
	finish
}

process_args $*
main
