#!/bin/bash 

set -e

# check pack
if ! type jq &> /dev/null ; then
	echo "Request jq!"
	exit
fi

sname='stuido'

windows_option='{
"dev": {"layout": "tiled","panes": ["", "", ""], "zoom": 2},
"work": {"panes": ["", ""]}
}'

# {
#	"window-name": {"layout": "layout-name", "panes": ["command", ""], "zoom": pane-number}
# }
#
# layout is optional.
# if you don't want let panes to execute the command, then let it be "".
# and the number of panes is equal to the length of the array.
# zoom is optional, zoom the pane of the specify pane number.


# ----------------------------------------

# sendKeys window-name panes-index
sendKeys(){
	cmd=$(echo $windows_option | jq -r .$1.panes[$2])
	tmux send-keys clear C-m
	[ -n "$cmd" ] && tmux send-keys "$cmd" C-m
	return 0
}

# setTitle window-name pane-number
setTitle(){
	tmux select-pane -T $1-$2
}

# createPanes window-name
createPanes(){
	# create panes
	panes=$(echo $windows_option | jq ".$1.panes | length")
	panes=$(( $panes-1 ))

	setTitle $1 0
	for j in $(seq $panes)
	do
		tmux split-window
		setTitle $1 $j

		# send keys to split-window-pane
		sendKeys $1 $j

	done
	return 0
}

createWindows(){
	# create windows
	for i in $(seq 0 $(( $windows_count-1 )))
	do

		if [ $i -eq 0 ]; then
			tmux new -d -s $sname -n ${windows[$i]}
		else
			tmux new-window -n ${windows[$i]}
		fi

		# send keys to first window-pane
		sendKeys ${windows[$i]} 0

		# create panes
		createPanes ${windows[$i]}

		# set windows layout
		window_layout=$(echo $windows_option | jq -r .${windows[$i]}.layout)
		[ "$window_layout" == "null" ] && window_layout="tiled"
		tmux select-layout $window_layout

		# zoom pane
		zoom_number=$(echo $windows_option | jq -r .${windows[$i]}.zoom)
		[ "$zoom_number" != "null" ] && tmux resize-pane -Z -t $zoom_number || tmux select-pane -t 0

	done

	tmux select-window -t 0
	return 0
}

# ----------------------------------------

windows_count=$(echo $windows_option | jq "length")

# get lists of windows' name
for l in $(seq 0 $(( $windows_count-1 )))
do
	windows[$l]=$(echo $windows_option | jq -r keys_unsorted[$l])
done

createWindows

tmux a -t $sname 
