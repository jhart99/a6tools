#!/usr/bin/env python3
"""  Frequency offset fix for AUCTUS A6 based radios

This program takes a measured frequency and a desired frequency and
then reads a TCXO error programmed into the radio and sets a new TCXO
offset in the radio.  The radio needs to have its channel changed
after for the new setting to take effect.

This fixes the high BER seen on some radios like my GOCOM GD900 which
had a 800 Hz offset from the factory which while within spec was
outside what my poor MMDVM board could tolerate.

"""

import serial
import binascii
import time
import struct
import sys
import functools
import operator
import a6

__author__ = "jhart99"
__license__ = "MIT"


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Auctus A6 Frequency Error Fixer')
    parser.add_argument('-p', '--port', default='/dev/ttyUSB0',
                        type=str, help='serial port')
    parser.add_argument('-b','--baudrate', default=921600,
                        type=int, help='baud rate')
    parser.add_argument('-v','--verbosity', default=0, action='count',
                        help='print sent and received frames to stderr for debugging')
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s 0.0.1',
                        help='display version information and exit')
    parser.add_argument('current', type=int,
                        help='the frequency the radio is currently transmitting in Hz')
    parser.add_argument('target', type=int,
                        help='the desired frequency in Hz')
    args = parser.parse_args()

    sio = serial.Serial(args.port, args.baudrate, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, xonxoff=True, rtscts=False, timeout = 0.001)
    sio.flush()

    delta = args.target - args.current
    curerr = a6.get_freq_err(sio)
    target = curerr + delta
    if abs(target) > 2500:
        raise ValueError("Desired offset exceeds maximum of 2500 Hz")
    a6.set_freq_err(sio, int((target + 2500)/10))

    # sys.stdout.buffer.write(data)
    sio.close()
