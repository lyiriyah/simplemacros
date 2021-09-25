#!/usr/bin/env python

from evdev import InputDevice, categorize, ecodes, events

import argparse
import asyncio
import os
import subprocess, shlex

debug = False

parser = argparse.ArgumentParser(description="Simple Linux-only macro program.")
parser.add_argument("--debug", action='store_true', help='Debugging mode for debugging purposes')
args = parser.parse_args()

def run(x):
    _ = subprocess.Popen(shlex.split(x))

is_shifted = False

shift_keys = ["KEY_LEFTSHIFT", "KEY_RIGHTSHIFT"]

keymap = {}
shift_keymap = {}

led = 2
event_handler = None

configfolder = os.environ['HOME'] + "/.config/"
configfile = configfolder + "simplemacros.conf"

if not os.path.exists(configfile):
    open(configfile, "w+").close()

with open(configfile, "r") as f:
    for num, line in enumerate(f):
        if args.debug: print(f"{num} | {line}")

        if line.startswith("var"): exec(' '.join(line.split()[1::]))
        elif line.startswith("set"):
            split_line = line.split()
            if split_line[1] == "led":
                led = int(split_line[2])
            elif split_line[1] == "event_handler":
                event_handler = split_line[2]
            else:
                print(f"error: {split_line[1]} not a recognised set option")
        elif len(line) == 0 or line.isspace() or line.startswith('#'): pass
        elif line.startswith("shift"):
            split_line = line.lstrip("shift ").split("=") 
            shift_keymap[str(split_line[0]).replace(" ", "")] = split_line[1]
        else:
            split_line = line.split('=')
            keymap[str(split_line[0]).replace(" ", "")] = split_line[1]

if args.debug:
    print(keymap)
    print(shift_keymap)

if event_handler is None:
    raise Exception("Event handler not provided")

dev = InputDevice("/dev/input/" + event_handler)
dev.grab()

try:
    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY:
            key = categorize(event)
            if key.keystate == key.key_up and key.keycode in shift_keys:
                if is_shifted:
                    dev.set_led(led, 0)
                    is_shifted = False
                else:
                    dev.set_led(led, 1)
                    is_shifted = True
            elif key.keystate == key.key_up and key.keycode not in shift_keys:
                try:
                    eval(shift_keymap[key.keycode]) if is_shifted else eval(
                            keymap[key.keycode])
                except KeyError:
                   print(f"shift+{key.keycode} isn't bound!") if is_shifted else print( f"{key.keycode} isn't bound!")
except (KeyboardInterrupt, ImportError):
    print("\nSimplemacros is exiting...")
    dev.ungrab
    del dev
    exit(0)
