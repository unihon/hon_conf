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

messOutPut(){
	echo -e "\n+<-----------------------------------------------------------+"
	echo -e " $@"
	echo -e "+----------------------------------------------------------->+\n"
}

autoHelp(){
	messOutPut "You can use: -y -p -s."
	return 0
}

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
	type $1 &> /dev/null && return 0 || return 1
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
	if [ "$OPT_p" == "y" ]; then
		messOutPut "Pack(s) ready, direct deploy vim!"
		return 0
	fi

	messOutPut "Check pack..."

	# check state.
	unPackList "${PACKS[@]}"
	if [ ${#PACK_UN_LIST[@]} -ne 0 ]; then
		if [ "$OPT_y" != "y"  ]; then
			messOutPut "The following pack(s) will be installed:\n" ${PACK_UN_LIST[@]}

			read -p "Confirm to continue? [y/n]: " sSkey
			if [ "$sSkey" == "n"  ]; then
				echo "Exit."
				exit
			fi
		fi
	else
		messOutPut "Pack(s) ready!"
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
		messOutPut "The following pack(s) is not install\n" ${PACK_UN_LIST[@]}

		read -p "Do you whant to try install again? [y/n/p]: " sSkey
		if [ "$sSkey" == "y" ]; then
			installPack
		elif [ "$sSkey" == "p" ]; then
			messOutPut "Pack(s) ready, direct deploy vim!"
		else
			echo "Exit."
			exit
		fi
	else
		messOutPut "Pack(s) ready!"
	fi
}

defPlugin(){
	DEF_PLUGIN=("scrooloose/nerdtree" "tpope/vim-commentary" "jiangmiao/auto-pairs")
	for i in ${DEF_PLUGIN[@]}
	do
		sed -r -i "s:^\"\s(Plug\s'${i}'$):\1:" ~/.vimrc
	done
}

selectPlugin(){
	plugins=$(whiptail \
		--title "Checklist vim plugin" \
		--checklist "" 13 39 6 \
		"scrooloose/nerdtree" "" ON \
		"tpope/vim-commentary" "" ON \
		"jiangmiao/auto-pairs" "" ON \
		"airblade/vim-gitgutter" "" OFF \
		"mattn/emmet-vim" "" OFF \
		"pangloss/vim-javascript" "" OFF \
		"posva/vim-vue" "" OFF \
		3>&1 1>&2 2>&3)

	if [ $? -eq 0 ]; then
		for i in $plugins
		do
			i=$(echo $i | sed -r 's:^"(.*)"$:\1:')
			sed -r -i "s:^\"\s(Plug\s'${i}'$):\1:" ~/.vimrc
		done
	else
		defPlugin
	fi
}

#---------------------------------

while getopts yps FLAG 2> /dev/null; do
	case $FLAG in
		y) OPT_y='y' ;;
		p) OPT_p='y' ;;
		s) OPT_s='y' ;;
		\?) autoHelp; exit 1 ;;
	esac
done

DIST=$(getDist); [ "$DIST" == "none" ] && echo "Don't know DIST." && exit

installPack

if type curl &> /dev/null; then
	curl -o ~/.vim/autoload/plug.vim --create-dirs "$VIM_PLUG" -o ~/.vimrc "$VIMRC"
else
	wget -P ~/.vim/autoload/ "$VIM_PLUG"; wget -O ~/.vimrc "$VIMRC"
fi

messOutPut "Configure files ready!"

[ "$OPT_s" == "y" ] && selectPlugin || defPlugin

vim -c PlugInstall -c qall

messOutPut "Complect!"
