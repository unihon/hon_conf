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
from os import getenv
from subprocess import run, PIPE, call

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

# check session for existence
def check_session(session_name):
    run_res = run(['tmux', 'ls', '-F', '#{session_name}'], stdout=PIPE, stderr=PIPE)
    if session_name in run_res.stdout.decode().split('\n'):
        # print('> session %s already exists.' % session_name)
        return True
    else:
        return False

def check_atach():
    if getenv('TMUX') is not None:
        return True
    else:
        return False


# set title
def set_title(pane_number, title):
    # may don't work on centos 7 when set default-terminal isn't screen* or tmux*,
    # pane title will restore or change when enter keys
    # set default-terminal to be screen* to fix it
    if pane_number is None:
        run(['tmux', 'select-pane', '-T', title])
    else:
        run(['tmux', 'select-pane', '-t', pane_number, '-T', title])
    return True


# set title on init
def set_title_init(window_item):
    for pane_number in range(len(WINDOWS_OPTION[window_item]['panes'])):
        title = WINDOWS_OPTION[window_item]['name'] + '-' + str(pane_number)
        set_title(str(pane_number), title)
    return True


def get_all_pane_number_in_window():
    run_res = run(['tmux', 'list-panes', '-F', '#{pane_index}'], stdout=PIPE)
    return run_res.stdout.decode().split('\n')[:-1]


def send_keys(pane_number, cmd):
    # if the software (eg: vim) can't run on a smaller terminal, an error may be reported
    # use `-h` horizontal split or add `sleep` to fix it
    exec_list = ['tmux', 'send-keys']
    if (cmd != ''):
        if pane_number is None:
            exec_list.extend([cmd, 'C-m'])
            run(exec_list)

        elif isinstance(pane_number, list):
            # need improve
            for _pane_number in pane_number:
                run(['tmux', 'send-keys', '-t', _pane_number, cmd, 'C-m'])

        else:
            exec_list.extend(['-t', pane_number, cmd, 'C-m'])
            run(exec_list)
    return True


# send keys init 
def send_keys_init(window_item):
    for pane_number in range(len(WINDOWS_OPTION[window_item]['panes'])):
        cmd = WINDOWS_OPTION[window_item]['panes'][pane_number]
        send_keys(str(pane_number), cmd)
    return True


def send_keys_all_pane_in_window(cmd):
    send_keys(get_all_pane_number_in_window(), cmd)
    return True


# create panes
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


# create windows
def create_windows(session_name):
    '''
    create sessions
    create windows
    '''

    for window_item in sorted(WINDOWS_OPTION.keys()):
        window_name = WINDOWS_OPTION[window_item]['name']

        if (window_item == 'w_0'):
            create_session(session_name, window_name)
        else:
            run(['tmux', 'new-window', '-n', window_name])

        # create panes
        create_panes(window_item)

        # set windows layout
        window_layout = WINDOWS_OPTION[window_item].get('layout', 'tiled')
        run(['tmux', 'select-layout', window_layout])

        # set title
        set_title_init(window_item)

        # send keys
        send_keys_init(window_item)

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
    if not check_atach():
        if not check_session(SESSION_NAME):
            create_windows(SESSION_NAME)
        run(['tmux', 'a', '-t', SESSION_NAME])
    else:
        print('> has attch')
    return True



# get var name from command line args, and get the var from locals var
if __name__ == '__main__':
    if len(sys.argv) > 1:
        # have args

        if sys.argv[1] == '-s':
            # studio
            try:
                WINDOWS_OPTION = locals()[sys.argv[2]]
                SESSION_NAME = sys.argv[2]
            except:
                WINDOWS_OPTION = locals()[DEFAULT_PROJECT]
                SESSION_NAME = DEFAULT_PROJECT
            run_fun()

        elif sys.argv[1] == '-t':
            # title
            try:
                title = sys.argv[2]
                set_title(None, title)
            except:
                pass

        elif sys.argv[1] == '-c':
            # command
            try:
                cmd = sys.argv[2]
            except:
                cmd = ''
            send_keys_all_pane_in_window(cmd)

        else:
            print('> args error')

    else:
        # default
        WINDOWS_OPTION = locals()[DEFAULT_PROJECT]
        SESSION_NAME = DEFAULT_PROJECT
        run_fun()

