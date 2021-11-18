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

from a6 import SerialIO, get_freq_err, set_freq_err

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
                        help='the measured frequency the radio is currently transmitting in Hz')
    parser.add_argument('target', type=int,
                        help='the programmed frequency in the radio in Hz')
    args = parser.parse_args()

    uart = SerialIO(args.port, args.baudrate, args.verbosity)

    delta = args.target - args.current
    curerr = get_freq_err()
    target = curerr + delta
    if abs(target) > 2500:
        raise ValueError("Desired offset exceeds maximum of 2500 Hz")
    set_freq_err(int((target + 2500)/10))