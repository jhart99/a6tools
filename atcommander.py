#!/usr/bin/env python3
"""  AT Commander for AUCTUS based radios

Allow for communication with AUCTUS A6 radios to their serial
interface through the debug interface.  Commands can either be "AT"
commands or "CPS" commands.  Both styles will work.

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
    parser = argparse.ArgumentParser(description='Auctus A6 ATECPS commander')
    parser.add_argument('-p', '--port', default='/dev/ttyUSB0',
                        type=str, help='serial port')
    parser.add_argument('-b','--baudrate', default=921600,
                        type=int, help='baud rate')
    parser.add_argument('-v','--verbosity', default=0, action='count',
                        help='print sent and received frames to stderr for debugging')
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s 0.0.1',
                        help='display version information and exit')
    parser.add_argument('command')
    args = parser.parse_args()

    sio = serial.Serial(args.port, args.baudrate, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, xonxoff=True, rtscts=False, timeout = 0.001)
    sio.flush()

    if args.command[0:3] == 'AT+':
        a6.send_ate_command(sio, args.command, args.verbosity)
    else:
        a6.send_cps_command(sio, bytes.fromhex(args.command), args.verbosity)
    a6.atecps_resp_read(sio)
    sio.close()
