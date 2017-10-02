#!/usr/bin/env python3

#
# this code is adapted from https://raw.githubusercontent.com/derekhe/waveshare-7inch-touchscreen-driver/master/touch_async.py
# it removes the x,y, and focuses purely on click handling
#

import struct
import time
import math
import glob
import uinput
import pyudev
import os
import asyncio


def check_device(thedevice):
    # USB id of my touchscreen
    if '483:5750' in (thedevice.get('DEVPATH')):
        print("Device found at: ", thedevice.device_node)
        with open(thedevice.device_node, 'rb') as f:
            print("Opening device and initiating mouse click emulation.")
            tasks.clear()
            tasks.append(asyncio.async(read_and_emulate_mouse(f)))
            loop.run_until_complete(asyncio.wait(tasks))
            print("Device async task terminated.")


@asyncio.coroutine
def async_read_data(fd, length):
    yield from asyncio.sleep(0)
    return fd.read(length)


@asyncio.coroutine
def read_and_emulate_mouse(fd):

    cnt = 0

    input_device = uinput.Device([
        uinput.BTN_LEFT,
        uinput.BTN_RIGHT,
        uinput.ABS_X,
        uinput.ABS_Y,
    ])

    clicked = False
    rightClicked = False
    (lastX, lastY) = (0, 0)
    startTime = time.time()

    while True:
        cnt = cnt + 1
        try:
            touch_data = yield from async_read_data(fd, 25)
            # print('Data' + ': ' + str(cnt) + ' - ' + str(len(touch_data)))
            if touch_data == 0:
                break;
        except IOError:
            return 0

        (tag, btnLeft, x, y) = struct.unpack_from('>c?HH', touch_data)
        print(btnLeft, x, y)

        if btnLeft:
            if not clicked:
                print("Left click.")
                input_device.emit(uinput.BTN_LEFT, 1)
                clicked = True
                startTime = time.time()
                (lastX, lastY) = (x, y)

            duration = time.time() - startTime
            movement = math.sqrt(pow(x - lastX, 2) + pow(y - lastY, 2))

            if clicked and (not rightClicked) and (duration > 1) and (movement < 20):
                print("Right click.")
                input_device.emit(uinput.BTN_RIGHT, 1)
                input_device.emit(uinput.BTN_RIGHT, 0)
                rightClicked = True
        else:
            print("Release.")
            clicked = False
            rightClicked = False
            input_device.emit(uinput.BTN_LEFT, 0)

    fd.close()


if __name__ == "__main__":
    os.system("modprobe uinput")

    tasks = []
    loop = asyncio.get_event_loop()

    context = pyudev.Context()
    print("Checking devices already plugged-in...")
    for device in context.list_devices(subsystem='hidraw'):
        check_device(device)

    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='hidraw')
    print("Waiting for touch device connection...")

    for device in iter(monitor.poll, None):
        print("HID device notification.  ACTION: ", device.get('ACTION'))

        if 'add' in (device.get('ACTION')):
            check_device(device)
