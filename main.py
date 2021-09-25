from evdev import InputDevice, categorize, ecodes, events

import os
import subprocess, shlex

run = lambda x: subprocess.run(shlex.split(x), preexec_fn=os.setpgrp)

is_shifted = False

shift_keys = ["KEY_LEFTSHIFT", "KEY_RIGHTSHIFT"]

keymap = {}
shift_keymap = {}

configfolder = os.environ['HOME'] + "/.config/"

configfile = configfolder + "simplemacros.conf"

with open(configfile, "r") as f:
    for num, line in enumerate(f):
        print(f"{num} | {line}")
        if line.startswith("var"):
            exec(' '.join(line.split()[1::]))
        elif len(line) == 0 or line.isspace() or line.startswith('#'):
            pass
        elif line.startswith("shift"):
            split_line = line.lstrip("shift ").split("=") 
            shift_keymap[str(split_line[0]).replace(" ", "")] = split_line[1]
        else:
            split_line = line.split('=')
            keymap[str(split_line[0]).replace(" ", "")] = split_line[1]

print(keymap)
print(shift_keymap)

dev = InputDevice("/dev/input/" + event_handler)

dev.grab()

for event in dev.read_loop():
    if event.type == ecodes.EV_KEY:
        key = categorize(event)
        if key.keystate == key.key_up and key.keycode in shift_keys:
            if is_shifted:
                dev.set_led(2, 0)
                is_shifted = False
            else:
                dev.set_led(2, 1)
                is_shifted = True
        elif key.keystate == key.key_up and key.keycode not in shift_keys:
            try:
                eval(shift_keymap[key.keycode]) if is_shifted else eval(keymap[key.keycode])
            except KeyError:
                print(f"shift+{key.keycode} isn't bound!") if is_shifted else print(f"{key.keycode} isn't bound!")
