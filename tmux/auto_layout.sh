#!/bin/bash 

set -e

sname='studio'

# create a new session and naming window
tmux new -d -s $sname -n dev

# split window, create a 'v' pane
tmux split-window -d -v

# zoom
tmux resize-pane -Z

# select pane
# tmux select-pane -t 0

# send key to pane
# tmux send-keys vim C-m

# ----------------------------

# create a new window
tmux new-window -d -n work

# select window
# tmux select-window -t 0

# attach to session
tmux a -t $sname 
