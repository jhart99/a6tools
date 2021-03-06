#!/usr/bin/env python3
""" Reboot and freeze

Reset the AUCTUS A6 processor and freeze execution.  This allows for
uninterupted dumping of the normally problematic BCPU rom.

"""

from a6 import SerialIO, reboot_and_freeze

__author__ = "jhart99"
__license__ = "MIT"


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Auctus A6 reboot and freeze')
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
    uart.write(reboot_and_freeze())