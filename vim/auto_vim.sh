#!/bin/bash

ISSUE_FILE="/etc/issue"
RELEASE_FILE="/etc/*-release"

PACK_GIT="git"
PACK_PYTHON="python"
PACKS=("$PACK_PYTHON" "$PACK_GIT")

VIMRC="https://raw.githubusercontent.com/unihon/hon_conf/master/vim/vimrc"
VIM_PLUG="https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim"

# distribution
DIST=""
# uninstall pack lists
PACK_UN_LIST=()

getDist(){
	if grep -iq "centos" $ISSUE_FILE $RELEASE_FILE; then
		echo "centos"
	elif grep -iq "debian" $ISSUE_FILE $RELEASE_FILE; then
		echo "debian"
	elif grep -iq "ubuntu" $ISSUE_FILE $RELEASE_FILE; then
		echo "ubuntu"
	else
		echo "none"
	fi
}

# check pack state.
checkPack(){
	[ "$1" == "" ] && return 0

	if [ "$DIST" == "centos" ]; then
		rpm -qa $1 | grep -iq "$1" && return 0 || return 1
	elif [ "$DIST" == "debian" -o "$DIST" == "ubuntu" ]; then
		dpkg -l | grep -iq "^ii\s.*\s$1" && return 0 || return 1
	else
		return 1
	fi
}

# get uninstall pack lists.
unPackList(){
	PACK_UN_LIST=()
	for i in "$@"
	do
		checkPack $i || PACK_UN_LIST=("${PACK_UN_LIST[@]}" "$i") 
	done
}

# install pack
installPack(){
	# check state.
	unPackList "${PACKS[@]}"
	if [ ${#PACK_UN_LIST[@]} -ne 0 ]; then
		if [ "$1" != "-y" ]; then
			echo "Will install this pack:" 
			echo -e "\n${PACK_UN_LIST[@]}\n" 
			echo -n "Confirm to continue? [y/n]: "

			read sSkey
			if [ "$sSkey" == "n" ]; then
				echo "Exit."
				exit
			fi
		fi
	else
		return 0	
	fi

	# install pack.
	if [ "$DIST" == "centos" ]; then
		yum -y install "${PACK_UN_LIST[@]}"
	elif [ "$DIST" == "debian" -o "$1" == "ubuntu" ]; then
		apt-get -y install "${PACK_UN_LIST[@]}"
	else
		return 1
	fi

	# check pack install state.
	unPackList "${PACKS[@]}"
	if [ ${#PACK_UN_LIST} -ne 0 ]; then
		echo "This pack is not install:" 
		echo -e "\n${PACK_UN_LIST[@]}\n" 
		echo -n "Do you whant to try install again? [y/n]: "
		read sSkey
		if [ "$sSkey" == "y" ]; then
			installPack
		else
			echo "Exit."
		fi
	fi
}

#---------------------------------

DIST=$(getDist); [ "$DIST" == "none" ] && echo "Don't know DIST." && exit

echo -e "\nCheck pack...\n"
installPack $1
echo -e "\nPack ready.\n"

mkdir -p ~/.vim/autoload/; wget -O ~/.vimrc "$VIMRC"; wget -O ~/.vim/autoload/plug.vim "$VIM_PLUG"
echo -e "\nConfigure file ready.\n"

echo -e "\nFinish!\n"
