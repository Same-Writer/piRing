#!/usr/bin/env python3

import subprocess
import sys, os, signal

# pkill signal values: https://linux.die.net/Bash-Beginners-Guide/sect_12_01.html
    # SIGTERM = 15 
    # SIGINT = 2

bashCommand = "sudo pkill -15 -f "
scriptToKill = "clock.py"

if len(sys.argv) > 1:
    scriptToKill = sys.argv[1]

fullCommand = bashCommand + scriptToKill

#print(fullCommand)

subprocess.call(fullCommand, shell=True)

# Catching KeyboardInterrupt in Python during program shutdown
# https://stackoverflow.com/questions/21120947/catching-keyboardinterrupt-in-python-during-program-shutdown

# https://stackoverflow.com/questions/13024532/simulate-ctrl-c-keyboard-interrupt-in-python-while-working-in-linux