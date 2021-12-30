from os import wait
import serial
import time
import sys
import re
from collections import deque

from a6.escaper import unescaper
from .eprint import eprint
from .a6commands import CPSFrame, h2p_command
from .a6commands import ChanInfoFrame, h2p_command
from .a6commands import ate_command
from .a6commands import cps_command
from .a6commands import read_uart_to_host
from .rdadebug import RdaFrame, rda_frames_from_bytes
from .rdadebug import read_word

class Singleton(object):
    def __new__(cls, *args, **kwargs):
        """ Singleton  class

        @param args:  arguments
        @param kwargs: keyword arguments 
        @return: object
        """
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.init(*args, **kwargs)
        return it

    def init(self, *args, **kwargs):
        """
        """
        pass

class SerialIO(Singleton):
    def init(self, port, baudrate=921600, verbosity=0, timeout=0.1):
        """ Initialize the serial port

        @param port: serial port
        @param baudrate: baud rate
        @param verbosity: verbosity level
        """
        self.port = port
        self.sio = serial.Serial(port, baudrate, 
            serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE,
            xonxoff=True, rtscts=False, timeout=timeout)
        self.verbosity = verbosity
        self._ate_cps_addr = 0
        self._ate_cps_resp_addr = 0
        self._ate_cps_resp_length_addr = 0
        self._uart_resp_addr = 0
        self.sio.flush()
        if verbosity > 0:
            eprint("SerialIO: {} initialized".format(self.port))

    def __del__(self):
        """ Close the serial port
        """
        self.sio.close()

    def write(self, msg):
        """ Write a message to the serial port

        @param msg: message
        """
        if self.verbosity > 0:
            eprint("write : ", msg.hex())
        self.sio.write(msg)

    def read(self, nbytes):
        """ Read nbytes from the serial port

        @param nbytes: number of bytes
        @return: message
        """
        data = self.sio.read(nbytes)
        if self.verbosity > 0:
            eprint("read  : ", data.hex())
        return data
    
    def flush(self):
        """ Flush the serial port
        """
        self.sio.flush()

    @property
    def in_waiting(self):
        """ return the number of bytes in the serial port
        """
        return self.sio.in_waiting

    @property
    def ate_cps_addr(self):
        """ return the address of the ate command
        """
        if self._ate_cps_addr == 0:
            self._ate_cps_addr = fetch_memory_address(0x81c00270)
            self._ate_cps_addr = int.from_bytes(self._ate_cps_addr, byteorder='little')
        return self._ate_cps_addr

    @property
    def ate_cps_resp_addr(self):
        """ return the address of the ate command response
        """
        if self._ate_cps_resp_addr == 0:
            self._ate_cps_resp_addr = fetch_memory_address(0x81c00264)
            self._ate_cps_resp_addr = int.from_bytes(self._ate_cps_resp_addr, byteorder='little')
        return self._ate_cps_resp_addr

    @property
    def ate_cps_resp_length_addr(self):
        """ return the address of the ate command response
        """
        return self.ate_cps_resp_addr - 4

    @property
    def uart_resp_addr(self):
        """ return the address of the ate command response
        """
        if self._uart_resp_addr == 0:
            self._uart_resp_addr = fetch_memory_address(0x81c0026c)
            self._uart_resp_addr = int.from_bytes(self._uart_resp_addr, byteorder='little')
        return self._uart_resp_addr



def write_flush_pause(msg, sleep = 0.07):
    """ Write out to serial and wait for the radio to process the command

    @param msg: bytes to write
    @param sleep: time to sleep after writing in ms

    """
    uart = SerialIO()
    uart.write(msg)
    uart.flush()
    time.sleep(0.07)


def send_ate_command(msg):
    """ Send a command to the ATE/CPS function on the radio

    To send a command to the ATE or CPS software on the radio, it has
    to be surrounded by these h2p commands which clear the registers
    and then throw and interupt which causes the command to be
    executed
    
    @param msg: bytes to write

    """
    uart = SerialIO()
    write_flush_pause(h2p_command(0))
    write_flush_pause(ate_command(uart.ate_cps_addr, msg))
    write_flush_pause(h2p_command(0xa5))

def send_cps_command(msg):
    """ Send a command to the ATE/CPS function on the radio

    To send a command to the ATE or CPS software on the radio, it has
    to be surrounded by these h2p commands which clear the registers
    and then throw and interupt which causes the command to be
    executed

    @param msg: bytes to write

    """

    uart = SerialIO()
    write_flush_pause(h2p_command(0))
    write_flush_pause(cps_command(uart.ate_cps_addr, msg))
    write_flush_pause(h2p_command(0xa5))

def wait_on_read(retries=256, delay=0.001):
    """ Wait until a read happens

    This function waits until something is received from the serial or
    will abort after a certain number of retries.

    @param retries: number of retries before aborting
    @param delay: time to sleep between retries
    """

    uart = SerialIO()
    size = uart.in_waiting
    countdown = retries
    while size == 0 and countdown > 0:
        size = uart.in_waiting
        countdown -= 1
        if delay: time.sleep(delay)
    if size > 0:
        data = uart.read(size)
    else:
        # nothing received
        data = b''
    return data

def send_uart_setup():
    """ Replays the initial UART setup sequence

    This sequence and timing is from the CPS software capture.
    """
    uart = SerialIO()
    knock_worked = False
    retries = 25
    while not knock_worked and retries > 0:
        uart.write(read_uart_to_host())
        uart.flush()
        time.sleep(0.001)
        data = wait_on_read()
        data = unescaper(data)
        response = RdaFrame(data)
        if response.seq == 1 and response.content == b'\x80':
            knock_worked = True
        else:
            time.sleep(0.25)
        retries -= 1
    return knock_worked

def fetch_memory_address(addr, seq=1):
    """ Attempt to read a memory address and keep trying until it succeeds

    """
    uart = SerialIO()
    read_ok = False
    retval = b''
    while not read_ok:
        out_frame = read_word(addr, seq)
        uart.write(out_frame)
        data = wait_on_read()
        data = unescaper(data)
        frames = rda_frames_from_bytes(data)
        for frame in frames:
            if frame is None:
                break
            if frame.seq == seq and not frame.check_fail:
                read_ok = True
                retval = frame.content
                break
    return retval

def fetch_memory_block(begin, end, offset = 0):
    """ Attempt to read a block of memory

    Note: The A6 takes about 15ms roundtrip from sending a request to receiving
    the reply.  We don't need to wait, there seems to be plenty of buffer for
    the commands. However, the reads have a number attached to them which can
    only go from 0 to 255 and 0 and 255 can't be used.  Generally everything
    works, but we need to be sure that we don't miss or corrupt things.
    
    @param begin: start address
    @param end: end address
    @return: list of bytes

    """
    uart = SerialIO()
    addr = begin
    data = b''
    out = [None] * ((end - begin)//4 + 1)

    seq = 1
    while addr < end:
        frame = read_word(addr, seq + offset)
        uart.write(frame)
        addr += 4
        seq += 1
        if uart.in_waiting > 0:
            data += uart.read(uart.in_waiting)

    time.sleep(0.025)
    while uart.in_waiting > 0:
        data += uart.read(uart.in_waiting)
    
    frames = rda_frames_from_bytes(data)
    for frame in frames:
        seq = frame.seq - 1 - offset
        if seq < 0:
            eprint('event: {:x}'.format(int.from_bytes(frame.content, 'little')))
            continue
        out[seq] = frame.content
    for idx, data in enumerate(out):
        if data is None:
            out[idx] = fetch_memory_address(begin + idx*4)

    return b''.join(out)

def atecps_resp_read():
    """ Read the response from an ATECPS command

    @return: response from ATECPS command

    """
    uart = SerialIO()
    length = fetch_memory_address(uart.ate_cps_resp_length_addr)
    length = int.from_bytes(length, 'little')
    response = read_mem_range(uart.ate_cps_resp_addr, uart.ate_cps_resp_addr + length)
    return response

def uart_resp_read():
    """ Read the response from an ATECPS command

    @return: response from ATECPS command

    """
    uart = SerialIO()
    length = fetch_memory_address(uart.uart_resp_addr)
    length = length[1]
    response = read_mem_range(uart.uart_resp_addr, uart.uart_resp_addr + length)
    return response

def read_mem_range(begin, end):
    """ Read a memory range

    @param begin: start address
    @param end: end address
    @return: the data in bytes

    """
    addr = begin
    datalist = []
    end = end + (end%4)
    offset = 0
    while addr < end:
        if end - addr > 0x100:
            block = 0x100
        else:
            block = end - addr

        data = fetch_memory_block(addr, addr + block, offset)
        datalist.append(data)
        addr += block
        offset = (offset + 0x40) % 0x80
    return b''.join(datalist)

def read_mem_range2(begin, end):
    """ Read a memory range

    @param begin: start address
    @param end: end address
    @return: the data in bytes

    """
    queued_reads = {}
    store = {}
    addr = begin
    seq = 1
    uart =  SerialIO()
    data = b''
    while addr < end:
        out_frame = read_word(addr, seq)
        queued_reads[seq] = addr
        uart.write(out_frame)
        while seq in queued_reads:
            seq += 1
            if seq == 255:
                seq = 1
        addr += 4
        if uart.in_waiting > 0:
            data += uart.read(uart.in_waiting)
            data = unescaper(data)
            frames = rda_frames_from_bytes(data)
            for frame in frames:
                if frame is None:
                    break
                if not frame.check_fail and frame.seq in queued_reads:
                        store[queued_reads[frame.seq]] = frame.content
                        print('{} : {}'.format(queued_reads[frame.seq], frame.content))
                        del queued_reads[frame.seq]




    return b''

def get_chan_info(channel = 0):
    """ Get the channel info

    @param channel: channel number
    @return: the channel info
    """
    cmd = bytes([0, 0x12]) + channel.to_bytes(1, 'little')
    send_cps_command(cmd)
    resp = uart_resp_read()
    print(ChanInfoFrame(resp))
    # sys.stdout.buffer.write(resp)

def get_freq_err():
    """ Get the frequency error from the Radio

    @return: frequency error in Hz
    """
    send_ate_command("AT+DMOCONNECT")
    send_ate_command("AT+GETFREQERR")
    resp = atecps_resp_read()
    resp = resp.split(b'\x00')
    resp = [x.decode('utf-8') for x in resp]
    return parse_freq_err_resp(resp[0])

def parse_freq_err_resp(resp):
    """ Parse the frequency error response

    @param resp: response from ATECPS
    @return: frequency error in Hz
    """
    pattern = '\[(.+)\]'
    freqerr = re.search(pattern, resp)
    if freqerr:
        return int(freqerr.group(1))
    else:
        return 0

def set_freq_err(freqerr):
    """ Set the frequency error on the Radio

    @param freqerr: frequency error parameter which is (-2500 + 10 * freqerr) in Hz

    """
    send_ate_command("AT+DMOCONNECT")
    send_ate_command("AT+DMOFREQERR={}".format(freqerr))
    resp = atecps_resp_read()
    resp = resp.split(b'\x00')
    resp = [x.decode('utf-8') for x in resp]
    for line in resp:
        print(line)
