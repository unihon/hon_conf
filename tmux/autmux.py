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
from subprocess import run, PIPE

# project list

light = {
        "w_0": {"name": "dev", "layout": "tiled", "panes": ["", ""], "zoom": 0},
        "w_1": {"name": "work", "layout": "tiled", "panes": [""]}
        }

studio = {
        "w_0": {"name": "dev", "layout": "tiled", "panes": ["", "", ""], "zoom": 2},
        "w_1": {"name": "work", "layout": "tiled", "panes": ["", ""]}
        }

DEFAULT_PROJECT = 'light'

# ----------------------------------------

# get var name from command line args, and get the var from locals var
try:
    WINDOWS_OPTION = locals()[sys.argv[1]]
    SESSION_NAME = sys.argv[1]
except:
    WINDOWS_OPTION = locals()[DEFAULT_PROJECT]
    SESSION_NAME = DEFAULT_PROJECT

# check session for existence
def check_session(session_name):
    run_res = run(['tmux', 'ls', '-F', '#{session_name}'], stdout=PIPE, encoding='UTF-8')
    if session_name in run_res.stdout.split('\n'):
        # print('> session %s already exists.' % session_name)
        return True
    else:
        return False


# set title window-name pane-number
def set_title(window_name, pane_number):
    # may don't work on centos 7 when set default-terminal isn't screen* or tmux*,
    # pane title will restore or change when enter keys
    # set default-terminal to be screen* to fix it
    run(['tmux', 'select-pane', '-T', window_name + '-' + str(pane_number)])

    return True


# send keys window-item
def send_keys(window_item):
    for pane_number in range(len(WINDOWS_OPTION[window_item]['panes'])):
        run(['tmux', 'select-pane', '-t', str(pane_number)])

        # set title
        set_title(WINDOWS_OPTION[window_item]['name'], pane_number)

        # if the software (eg: vim) can't run on a smaller terminal, an error may be reported
        # use `-h` horizontal split or add `sleep` to fix it
        cmd = WINDOWS_OPTION[window_item]['panes'][pane_number]
        if (cmd != ""):
            run(['tmux', 'send-keys', 'clear', 'C-m'])
            run(['tmux', 'send-keys', cmd, 'C-m'])

    return True


# create panes window-item
def create_panes(window_item):
    for pane_number in range(len(WINDOWS_OPTION[window_item]['panes'])-1):
        # maybe no enough space for new pane
        # if you want more panes, you can use `-h` horizontal split
        run(['tmux', 'split-window', '-p', '100'])

    return True


# create session
def create_session(session_name, window_name):
    run(['tmux', 'new', '-d', '-s', session_name, '-n', window_name])

    return True


# create windows session-name
def create_windows(SESSION_NAME):
    '''
    create sessions
    create windows
    '''

    for window_item in sorted(WINDOWS_OPTION.keys()):
        window_name = WINDOWS_OPTION[window_item]['name']

        if (window_item == 'w_0'):
            create_session(SESSION_NAME, window_name)
        else:
            run(['tmux', 'new-window', '-n', window_name])

        # create panes
        create_panes(window_item)

        # set windows layout
        window_layout = WINDOWS_OPTION[window_item].get('layout', 'tiled')
        run(['tmux', 'select-layout', window_layout])

        # send keys and set title
        send_keys(window_item)

        # zoom pane or select pane
        if (WINDOWS_OPTION[window_item].__contains__('zoom')):
            run(['tmux', 'resize-pane', '-Z', '-t', str(WINDOWS_OPTION[window_item]['zoom'])])
        elif (WINDOWS_OPTION[window_item].__contains__('active')):
            run(['tmux', 'select-pane', '-t', str(WINDOWS_OPTION[window_item]['active'])])
        else:
            run(['tmux', 'select-pane', '-t', '0'])

    run(['tmux', 'select-window', '-t', '0'])

    return True


def run_fun():
    if not check_session(SESSION_NAME):
        create_windows(SESSION_NAME)
        run(['tmux', 'a', '-t', SESSION_NAME])
    else:
        run(['tmux', 'a', '-t', SESSION_NAME])


if __name__ == '__main__':
    run_fun()
