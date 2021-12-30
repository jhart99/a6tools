#!/usr/bin/env python3
"""  CPS reader for AUCTUS based radios
"""

import argparse
import asyncio
from a6.serialasyncio import RdaDebugSerialInterface
__author__ = "jhart99"
__license__ = "MIT"

async def main(args):
    """ main function
    """
    # create the serial interface
    serial = RdaDebugSerialInterface(args)
    await serial.init_preamble()
    # read the CPS
    dump = await serial.read_cps()
    await serial.finalizer()
    # print/write out the data
    with open(args.out, 'wb') as f:
        f.write(dump)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Auctus A6 CPS reader')
    parser.add_argument('-o', '--out', default='/dev/stdout',
                        type=str, help='output data to')
    parser.add_argument('-p', '--port', default='/dev/ttyUSB0',
                        type=str, help='serial port')
    parser.add_argument('-b','--baudrate', default=921600,
                        type=int, help='baud rate')
    parser.add_argument('-v','--verbose', default=0, action='count',
                        help='print sent and received frames to stderr for debugging')
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s 0.0.1',
                        help='display version information and exit')
    args = parser.parse_args()

    # start the asyncio loop
    asyncio.run(main(args))
