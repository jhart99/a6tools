import serial
import time
import sys
from .eprint import eprint
from .a6commands import h2p_command
from .a6commands import ate_command
from .a6commands import cps_command
from .a6commands import read_uart_to_host
from .rdadebug import RdaFrame
from .rdadebug import read_word


def write_flush_pause(sio, msg, verbosity=0):
    """ Write out to serial and wait for the radio to process the command
    """
    sio.write(msg)
    if verbosity: eprint(">" + msg.hex())
    sio.flush()
    time.sleep(0.07)


def send_ate_command(sio, msg, verbosity=0):
    """ Send a command to the ATE/CPS function on the radio

    To send a command to the ATE or CPS software on the radio, it has
    to be surrounded by these h2p commands which clear the registers
    and then throw and interupt which causes the command to be
    executed

    """
    sio.write(read_word(0x81c00270))
    atecps_addr = fetch_memory_address(sio, 0x81c00270, verbosity)

    write_flush_pause(sio, h2p_command(0), verbosity)
    write_flush_pause(sio, ate_command(msg, atecps_addr), verbosity)
    write_flush_pause(sio, h2p_command(0xa5), verbosity)

def send_cps_command(sio, msg, verbosity=0):
    """ Send a command to the ATE/CPS function on the radio

    To send a command to the ATE or CPS software on the radio, it has
    to be surrounded by these h2p commands which clear the registers
    and then throw and interupt which causes the command to be
    executed

    """
    atecps_addr = fetch_memory_address(sio, 0x81c00270, verbosity)

    write_flush_pause(sio, h2p_command(0), verbosity)
    write_flush_pause(sio, cps_command(msg, atecps_addr), verbosity)
    write_flush_pause(sio, h2p_command(0xa5), verbosity)

def wait_on_read(sio, retries=256, delay=0, verbosity = 0):
    """ Wait until a read happens

    This function waits until something is received from the serial or
    will abort after a certain number of retries.
    """

    size = sio.in_waiting
    countdown = retries
    while size == 0 and countdown > 0:
        size = sio.in_waiting
        countdown -= 1
        if delay: time.sleep(delay)
    if countdown == 0:
        # nothing received
        return b''
    if size > 0:
        data = sio.read(size)
        if verbosity: eprint(">" + data.hex())
    return data

def send_uart_setup(sio, verbosity=0):
    """ Replays the initial UART setup sequence

    This sequence and timing is from the CPS software capture.
    """
    knock_worked = False
    retries =25
    while not knock_worked and retries > 0:
        sio.write(read_uart_to_host())
        if verbosity: eprint(">" + read_uart_to_host().hex())
        sio.flush()
        time.sleep(0.001)
        data = wait_on_read(sio)
        if verbosity: eprint("<" + data.hex())
        response = RdaFrame(data)
        eprint(response)
        if response.seq == 1 and response.content == b'\x80':
            knock_worked = True
        else:
            if verbosity: eprint('no data')
            time.sleep(0.25)
        retries -= 1
    return knock_worked

def fetch_memory_address(sio, addr, seq=1, verbosity = 0):
    """ Attempt to read a memory address and keep trying until it succeeds

    """
    readOk = False
    retval = b''
    retries = 25
    while not readOk:
        frame = read_word(addr, seq)
        if verbosity: eprint(">" + frame.hex())
        sio.write(frame)
        sio.flush()
        size = sio.in_waiting
        i = retries
        while size == 0 and i > 0:
            time.sleep(0.001)
            size = sio.in_waiting
            i -= 1
        if retries == 0:
            if verbosity: eprint('no data')
            continue
        data = sio.read(size)
        if verbosity: eprint("<" + data.hex())
        inboundFrame = RdaFrame(data)
        readOk = inboundFrame.seq == seq and not inboundFrame.check_fail
        retval = inboundFrame.content
    return retval

def atecps_resp_read(sio, verbosity = 0):
    """ Read the response from an ATECPS command

    """
    atecps_resp_addr = fetch_memory_address(sio, 0x81c00264, verbosity)
    atecps_resp_addr = int.from_bytes(atecps_resp_addr, 'little')
    length = fetch_memory_address(sio, atecps_resp_addr - 4, verbosity)
    length = int.from_bytes(length, 'little')
    read_mem_range(sio, atecps_resp_addr, atecps_resp_addr + length, verbosity)

def read_mem_range(sio, begin, end, verbosity=0 ):
    """ Read a memory range

    """
    addr = begin
    while addr < end:
        data = fetch_memory_address(sio, addr, verbosity)
        if len(data) == 4:
            sys.stdout.buffer.write(data)
            addr = addr + 4
