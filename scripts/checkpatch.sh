#!/bin/bash
set -e

pack_loader_image()
{
	local files ini

	files=`ls ./RKBOOT/*MINIALL*.ini`
	for ini in ${files}
	do
		if [ -f "${ini}" ]; then
			# Ignore unused
			if [ "${ini}" = "./RKBOOT/RK302AMINIALL.ini" -o \
				 "${ini}" = "./RKBOOT/RK30BMINIALL.ini" -o \
				 "${ini}" = "./RKBOOT/RK30MINIALL.ini" -o \
				 "${ini}" = "./RKBOOT/RK310BMINIALL.ini" ]; then
				continue;
			fi

			if grep  -q '^PATH=img/' ${ini}; then
				continue;
			fi

			echo "pack Input: ${ini}"
			./tools/boot_merger ${ini}
			rm -f *loader*.bin *download*.bin *idblock*.img
			echo
		fi
	done
}

pack_trust_image()
{
	local files ini TOS TOS_TA

# Pack 32-bit trust
	files=`ls ./RKTRUST/*TOS*.ini`
	for ini in ${files}
	do
		if ! test -s ${ini}; then
			continue;
		elif ! grep  -q '^TOS/' ${ini}; then
			continue;
		elif grep  -q '^PATH=img/' ${ini}; then
			continue;
		fi

		if [ -f "${ini}" ]; then
			echo "pack Input: ${ini}"

			# Parse orignal path
			TOS=`sed -n "/TOS=/s/TOS=//p" ${ini}|tr -d '\r'`
			TOS_TA=`sed -n "/TOSTA=/s/TOSTA=//p" ${ini}|tr -d '\r'`

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
		fi
	done

# Pack 64-bit trust
	files=`ls ./RKTRUST/*TRUST*.ini`
	for ini in ${files}
	do
		if grep  -q '^PATH=img/' ${ini}; then
			continue;
		fi

		if [ -f "${ini}" ]; then
			echo "pack Input: ${ini}"
			./tools/trust_merger ${ini}
			rm trust*.img
			echo
		fi
	done
}

check_dirty()
{
	for file in `find -name '*spl*.bin' -o -name '*tpl*.bin' -o -name '*usbplug*.bin'`; do
		if strings ${file} | grep '\-dirty ' ; then
			echo "ERROR: ${file} is dirty"
			exit 1
		fi
	done
}

check_stripped()
{
	for elf in `find -name '*bl31*.elf'`; do
		info=`file ${elf}`
		if echo ${info} | grep -q "not stripped" ; then
			echo "ERROR: ${elf} is not stripped"
			exit 1
		fi
	done
}

finish()
{
	echo "Packing loader and trust successfully."
	echo
}

check_dirty
check_stripped
pack_loader_image
pack_trust_image
finish
