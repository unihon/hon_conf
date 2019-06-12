#!/usr/bin/python3

# tmux 3.0-rc
#
# {
#     "window-item": {
#         "name": "window-name",
#         "layout": "layout-name",
#         "panes": ["command", ""],
#         "active": pane-number,
#         "zoom": pane-number
#     }
# }
# 
# window-item is used to sort windows.
# layout is optional.
# if you don't want let panes to execute the command, then let it be "".
# and the number of panes is equal to the length of the array.
# zoom and active is optional, zoom or active the pane of the specify pane number, and zoom is more preferred.
#
# note: execute `:%s/run/call/g` on vim make it compatible with python2

# ----------------------------------------

import sys
from subprocess import run

# project list

light = {
        "w_0": {"name": "dev", "layout": "tiled", "panes": ["", ""]},
        "w_1": {"name": "work", "layout": "tiled", "panes": [""]}
        }

studio = {
        "w_0": {"name": "dev", "layout": "tiled", "panes": ["", "", ""], "zoom": 2},
        "w_1": {"name": "work", "layout": "tiled", "panes": ["", ""]}
        }

DEFAULT_PROJECT = 'light'

# ----------------------------------------

try:
    WINDOWS_OPTION = locals()[sys.argv[1]]
    SESSION_NAME = sys.argv[1]
except:
    WINDOWS_OPTION = locals()[DEFAULT_PROJECT]
    SESSION_NAME = DEFAULT_PROJECT


# sendKeys window-item pane-number
def sendKeys(window_item, pane_number):
    cmd = WINDOWS_OPTION[window_item]['panes'][pane_number]

    if (cmd != ""):
        run(['tmux', 'send-keys', 'clear', 'C-m'])
        run(['tmux', 'send-keys', cmd, 'C-m'])

    return 0


# setTitle window-name pane-number
def setTitle(window_name, pane_number):
    # may don't work on centos 7 when set default-terminal isn't screen* or tmux*,
    # pane title will restore or change when enter keys
    # set default-terminal to be screen* to fix it
    run(['tmux', 'select-pane', '-T', window_name + '-' + str(pane_number)])

    return 0


# createPanes window-item
def createPanes(window_item):
    # set title for first window-pane
    setTitle(WINDOWS_OPTION[window_item]['name'], 0)

    for pane_number in range(1, len(WINDOWS_OPTION[window_item]['panes'])):
        # maybe no enough space for new pane
        run(['tmux', 'split-window', '-p', '100'])
        setTitle(WINDOWS_OPTION[window_item]['name'], pane_number)

        # send keys to split-window-pane
        sendKeys(window_item, pane_number)

    return 0


# createWindows session-name
def createWindows(SESSION_NAME):
    # create windows
    for window_item in sorted(WINDOWS_OPTION.keys()):
        window_name = WINDOWS_OPTION[window_item]['name']

        if (window_item == 'w_0'):
            run(['tmux', 'new', '-d', '-s', SESSION_NAME, '-n', window_name])
        else:
            run(['tmux', 'new-window', '-n', window_name])

        # send keys to first window-pane
        sendKeys(window_item, 0)

        # create panes
        createPanes(window_item)

        # set windows layout
        window_layout = WINDOWS_OPTION[window_item].get('layout', 'tiled')
        run(['tmux', 'select-layout', window_layout])

        # zoom pane or select pane
        if (WINDOWS_OPTION[window_item].__contains__('zoom')):
            run(['tmux', 'resize-pane', '-Z', '-t', str(WINDOWS_OPTION[window_item]['zoom'])])
        elif (WINDOWS_OPTION[window_item].__contains__('active')):
            run(['tmux', 'select-pane', '-t', str(WINDOWS_OPTION[window_item]['active'])])
        else:
            run(['tmux', 'select-pane', '-t', '0'])

    run(['tmux', 'select-window', '-t', '0'])

    return 0


# ----------------------------------------

createWindows(SESSION_NAME)
run(['tmux', 'a', '-t', SESSION_NAME])
