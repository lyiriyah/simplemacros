import evdev

worked = []

dev = evdev.InputDevice("/dev/input/event12")

for i in range(1, 33):
    print(f"Testing LED {i}")
    dev.set_led(i, 1)
    
    if input("Did it work?").lower() not in ["n", "no"]:
        worked.append(i)
    else:
        continue
    dev.set_led(i, 0)

print(f"The lights that lit up were {worked}")
