import functools
import operator
from .escaper import escaper
from .escaper import unescaper
from .eprint import eprint

__author__ = "jhart99"
__license__ = "MIT"

def compute_check(msg):
    """ Compute the check value for a message

    AUCTUS messages use a check byte which is simply the XOR of all
    the values of the message.

    """

    if len(msg) == 0:
        return int(0).to_bytes(1, 'little')
    return functools.reduce(operator.xor, msg).to_bytes(1, 'little')

def rda_debug_frame(flow, cmd, message):
    """ Format a raw message into a frame

    AUCTUS frames are of the form AD 00 XX FF ...message... YY
    where XX is the length of the message and YY is the check byte
    Additionally certain bytes in the message are escaped.

    """

    header = int(0xad).to_bytes(1, 'big')
    msg = flow + cmd + message
    msglen = len(msg).to_bytes(2, 'big')
    check = compute_check(msg)
    return escaper(header + msglen + msg + check)

def read_word(addr, seq = 1):
    """ make a frame to read a word at a memory address

    this function creates a frame to read the memory from the device
    suitable for serial transmission.

    """

    flow = bytes([0xff])
    command = bytes([0x02])
    if isinstance(addr, int):
        addr = addr.to_bytes(4, 'little')
    msg = addr + seq.to_bytes(1, 'big')
    return rda_debug_frame(flow, command, msg)

def write_register_int8(addr, msg):
    """ write to a byte to an internal register

    this function creates a frame to do some device magic and these
    frames are used in the preamble and finalizer commands.

    """

    flow = bytes([0xff])
    command = bytes([0x84])
    msg = addr.to_bytes(4, 'little') + msg.to_bytes(1, 'little')
    return rda_debug_frame(flow, command, msg)

def read_register_int8(addr, seq=1):
    """ make a frame containing a knock command

    this function creates a frame that I assume wakes up the device
    for further commands.

    """

    flow = bytes([0xff])
    command = bytes([0x04])
    msg = addr.to_bytes(4, 'little') + seq.to_bytes(1, 'big')
    return rda_debug_frame(flow, command, msg)

def write_block(addr, msg):
    """ make a frame containing a write command

    this function creates a frame to do write a multiple byte content
    at a specific memory address.  The length need not be a word, but
    could be 16 bytes or more.

    """

    flow = bytes([0xff])
    command = bytes([0x83])
    if isinstance(addr, int):
       addr = addr.to_bytes(4, 'little')
    msg = addr + msg
    return rda_debug_frame(flow, command, msg)


class RdaFrame:
    """ Received Frame class

    This class decodes possible received Frames.
    """
    ack = False
    check_fail = False
    seq = 0
    length = 0
    content = bytes([])
    def __init__(self, msg):
        if len(msg) <= 4:
            if(msg == b'\x11\x13'):
                self.ack = True
            else:
                # impossibly short frame something is wrong.
                self.check_fail = True
            return
        if (msg[-1].to_bytes(1, 'big') != compute_check(msg[3:-1])):
            self.check_fail = True
            return
        self.seq = msg[4]
        self.length = msg[2]
        self.content = msg[5:-1]
    def __repr__(self):
        return 'packet length {} seq {} content {} ack {} check_fail {}'.format(self.length, self.seq, self.content, self.ack, self.check_fail)

def rda_frame_parser(data):
    i = 0
    while data[i] != 0xad:
        i += 1
        if i >= len(data):
            return (None, b'')
    if len(data) < 4:
        return (None, data)
    frame_len = data[2]
    return (RdaFrame(data[i:4+frame_len+i]), data[frame_len+i+4:])

def rda_frames_from_bytes(data):
    out = []
    data = unescaper(data)
    while (len(data) > 0):
        frame, data = rda_frame_parser(data)
        out.append(frame)
    return out