#!/usr/bin/env python3
"""  AT Commander for AUCTUS based radios

Allow for communication with AUCTUS A6 radios to their serial
interface through the debug interface.  Commands can either be "AT"
commands or "CPS" commands.  Both styles will work.

"""

import serial
import sys
from a6 import read_mem_range, SerialIO


__author__ = "jhart99"
__license__ = "MIT"


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Auctus A6 dumper')
    parser.add_argument('--begin', type=lambda x: int(x,0),
                        help='begin address default 0x82000000',
                        default=0x82000000)
    parser.add_argument('--end', type=lambda x: int(x,0),
                        help='end address default 0x8200ff00',
                        default=0x8200ff00)
    parser.add_argument('-p', '--port', default='/dev/ttyUSB0',
                        type=str, help='serial port')
    parser.add_argument('-b','--baudrate', default=921600,
                        type=int, help='baud rate')
    parser.add_argument('-v','--verbosity', default=0, action='count',
                        help='print sent and received frames to stderr for debugging')
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s 0.0.1',
                        help='display version information and exit')
    args = parser.parse_args()

    uart = SerialIO(args.port, args.baudrate, args.verbosity)
    data = read_mem_range(args.begin, args.end)
    sys.stdout.buffer.write(data)
