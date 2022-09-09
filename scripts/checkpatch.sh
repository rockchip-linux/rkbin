#!/bin/bash
set -e

function pack_loader_image()
{
	for FILE in `ls ./RKBOOT/*MINIALL*.ini`
	do
		if [ "${FILE}" = "./RKBOOT/RK302AMINIALL.ini" -o \
			 "${FILE}" = "./RKBOOT/RK30BMINIALL.ini" -o \
			 "${FILE}" = "./RKBOOT/RK30MINIALL.ini" -o \
			 "${FILE}" = "./RKBOOT/RK310BMINIALL.ini" ]; then
			continue;
		fi

		if grep -q '^PATH=img/' ${FILE}; then
			continue;
		fi

		echo "Pack loader: ${FILE}"
		./tools/boot_merger ${FILE}
		rm -f *loader*.bin *download*.bin *idblock*.img
		echo
	done
}

function pack_trust_image()
{
	# Pack 32-bit trust
	for FILE in `ls ./RKTRUST/*TOS*.ini`
	do
		if ! test -s ${FILE}; then
			continue;
		elif ! grep -q 'TOS' ${FILE}; then
			continue;
		elif grep -q '^PATH=img/' ${FILE}; then
			continue;
		fi

		echo "Pack trust: ${FILE}"
		# Parse orignal path
		TOS=`sed -n "/TOS=/s/TOS=//p" ${FILE}|tr -d '\r'`
		TOS_TA=`sed -n "/TOSTA=/s/TOSTA=//p" ${FILE}|tr -d '\r'`

		# replace "./tools/rk_tools/" with "./" to compatible legacy ini content of rkdevelop branch
		TOS=$(echo ${TOS} | sed "s/tools\/rk_tools\//\.\//g")
		TOS_TA=$(echo ${TOS_TA} | sed "s/tools\/rk_tools\//\.\//g")

		if [ x${TOS_TA} != x -a x${TOS} != x ]; then
			./tools/loaderimage --pack --trustos ${TOS} ./trust.img 0x68400000
			./tools/loaderimage --pack --trustos ${TOS_TA} ./trust_with_ta.img 0x68400000
		elif [ ${TOS} ]; then
			./tools/loaderimage --pack --trustos ${TOS} ./trust.img 0x68400000
		elif [ ${TOS_TA} ]; then
			./tools/loaderimage --pack --trustos ${TOS_TA} ./trust.img 0x68400000
		else
			exit 1
		fi
		rm -f trust*.img
		echo
	done

	# Pack 64-bit trust
	for FILE in `ls ./RKTRUST/*TRUST*.ini`
	do
		if grep -q '^PATH=img/' ${FILE}; then
			continue;
		fi

		echo "Pack trust: ${FILE}"
		./tools/trust_merger ${FILE}
		rm -f trust*.img
		echo
	done
}

function check_dirty()
{
	for FILE in `find -name '*spl*.bin' -o -name '*tpl*.bin' -o -name '*usbplug*.bin'`; do
		echo "Checking dirty: ${FILE}"
		if strings ${FILE} | grep '\-dirty ' ; then
			echo "ERROR: ${FILE} is dirty"
			exit 1
		fi
	done
}

function check_stripped()
{
	for FILE in `find -name '*bl31*.elf'`; do
		echo "Checking strip: ${FILE}"
		INFO=`file ${FILE}`
		if echo ${INFO} | grep -q "not stripped" ; then
			echo "ERROR: ${FILE} is not stripped"
			exit 1
		fi
	done
}

function finish()
{
	echo "Packing loader and trust successfully."
	echo
}

check_dirty
check_stripped
pack_loader_image
pack_trust_image
finish
