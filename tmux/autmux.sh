#!/bin/bash 

set -e

# check pack
type jq &> /dev/null || echo "Request jq!"

sname='stuido'

windows_option='{
"dev": {"layout": "tiled","panes": ["", "", ""]},
"work": {"panes": ["", ""]}
}'

# {
#	"window": {"layout": "layout-name", "panes": ["command", ""]}
# }
#
# layout is optional
# if you don't want let panes to execute the command, then let it be "".
# and the number of panes is equal to the length of the array


# ----------------------------------------

echo "-------------------------
doing...
-------------------------"

windows_count=$(echo $windows_option | jq "length")

# get lists of windows' name
for l in $(seq 0 $(( $windows_count-1 )))
do
	windows[$l]=$(echo $windows_option | jq -r keys_unsorted[$l])
done

# create windows
for i in $(seq 0 $(( $windows_count-1 )))
do

	if [ $i -eq 0 ]; then
		tmux new -d -s $sname -n ${windows[$i]}
	else
		tmux new-window -n ${windows[$i]}
	fi

	# send keys to first window-pane
	cmd=$(echo $windows_option | jq -r .${windows[$i]}.panes[0])
	tmux send-keys clear C-m
	[ -n "$cmd" ] && tmux send-keys "$cmd" C-m

	# create panes
	panes=$(echo $windows_option | jq ".${windows[$i]}.panes | length")
	panes=$(( $panes-1 ))
	for j in $(seq $panes)
	do
		tmux split-window

		# send keys to split-window-pane
		cmd=$(echo $windows_option | jq -r .${windows[$i]}.panes[$j])
		tmux send-keys clear C-m
		[ -n "$cmd" ] && tmux send-keys "$cmd" C-m
	done

	# set windows layout
	window_layout=$(echo $windows_option | jq -r .${windows[$i]}.layout)
	[ "$window_layout" == "null" ] && window_layout="tiled"
	tmux select-layout $window_layout
done

tmux select-window -t 0
tmux select-pane -t 0
tmux a -t $sname 
