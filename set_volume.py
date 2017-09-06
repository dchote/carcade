#!/usr/bin/env python

import serial
picade = serial.Serial('/dev/ttyACM0',9600,timeout=1)

picade.write('l')

volume_target = 16

for x in range(1, volume_target):
    picade.write('+')