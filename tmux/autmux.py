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

from subprocess import run

SESSION_NAME = 'studio'
WINDOWS_OPTION = {
        "w_0": {"name": "dev", "layout": "tiled", "panes": ["", "", ""], "zoom": 2},
        "w_1": {"name": "work", "layout": "tiled", "panes": ["", ""]}
        }


# sendKeys window-item pane-number
def sendKeys(window_item, pane_number):
    cmd = WINDOWS_OPTION[window_item]['panes'][pane_number]

    if (cmd != ""):
        run(['tmux', 'send-keys', 'clear', 'C-m'])
        run(['tmux', 'send-keys', cmd, 'C-m'])

    return 0


# setTitle window-name pane-number
def setTitle(window_name, pane_number):
    run(['tmux', 'select-pane', '-T', window_name + '-' + str(pane_number)])


# createPanes window-item
def createPanes(window_item):
    # set title for first window-pane
    setTitle(WINDOWS_OPTION[window_item]['name'], 0)

    for pane_number in range(1, len(WINDOWS_OPTION[window_item]['panes'])):
        # maybe no enough space for new pane
        run(['tmux', 'split-window', '-h', '-p', '100'])
        setTitle(WINDOWS_OPTION[window_item]['name'], pane_number)

        # send keys to split-window-pane
        sendKeys(window_item, pane_number)

    return 0


# createWindows session-name
def createWindows(SESSION_NAME):
    # create windows
    for window_item in sorted(WINDOWS_OPTION.keys()):
        window_name = WINDOWS_OPTION[window_item]['name']

        if (window_name == WINDOWS_OPTION['w_0']['name']):
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
