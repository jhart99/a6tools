#!/usr/bin/env python3
"""  AT Commander for AUCTUS based radios

Allow for communication with AUCTUS A6 radios to their serial
interface through the debug interface.  Commands can either be "AT"
commands or "CPS" commands.  Both styles will work.

"""

import time
from a6 import send_ate_command, send_cps_command, atecps_resp_read, SerialIO

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

    uart = SerialIO(args.port, args.baudrate, args.verbosity)

    if args.command[0:3] == 'AT+':
        send_ate_command(args.command)
    else:
        send_cps_command(bytes.fromhex(args.command))
    time.sleep(0.1)
    data = atecps_resp_read()
    data = data.split(b'\x00')
    for line in data:
        print(line.decode('utf-8'))
