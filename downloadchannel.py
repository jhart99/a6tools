#!/usr/bin/env python3
"""  AT Commander for AUCTUS based radios

Allow for communication with AUCTUS A6 radios to their serial
interface through the debug interface.  Commands can either be "AT"
commands or "CPS" commands.  Both styles will work.

"""

from a6 import get_chan_info, SerialIO

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
    parser.add_argument('channel', type=int, help='channel number')
    args = parser.parse_args()


    uart = SerialIO(args.port, args.baudrate, args.verbosity)
    get_chan_info(args.channel)
