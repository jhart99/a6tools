import serial
import time
import sys
import re
from .eprint import eprint
from .a6commands import CPSFrame, h2p_command
from .a6commands import ChanInfoFrame, h2p_command
from .a6commands import ate_command
from .a6commands import cps_command
from .a6commands import read_uart_to_host
from .rdadebug import RdaFrame
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
    write_flush_pause(ate_command(msg, uart.ate_cps_addr))
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
    write_flush_pause(cps_command(msg, uart.ate_cps_addr))
    write_flush_pause(h2p_command(0xa5))

def wait_on_read(retries=256, delay=0):
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
    if countdown == 0:
        # nothing received
        return b''
    if size > 0:
        data = uart.read(size)
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
    retries = 25
    while not read_ok:
        frame = read_word(addr, seq)
        uart.write(frame)
        uart.flush()
        size = uart.in_waiting
        i = retries
        while size == 0 and i > 0:
            time.sleep(0.001)
            size = uart.in_waiting
            i -= 1
        if retries == 0:
            continue
        data = uart.read(size)
        inbound_frame = RdaFrame(data)
        read_ok = inbound_frame.seq == seq and not inbound_frame.check_fail
        retval = inbound_frame.content
    return retval

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
    while addr < end:
        data = fetch_memory_address(addr)
        if len(data) == 4:
            datalist.append(data)
            addr = addr + 4
    return b''.join(datalist)

def read_mem_burst(sio, begin, end, offset=0, verbosity=0):
    """ Read a limited memory range using a burst read

    @param sio: serial object
    @param begin: start address
    @param end: end address
    @param offset: offset of the sequence number
    @param verbosity: verbosity level
    @return: the data in bytes
    """
    
    if end - begin > 0x100:
        raise ValueError('burst read only supports ranges of less than 256 bytes')
    # the burst is in words of 4 bytes
    burst = (end - begin) / 4
    # preallocate the lists
    recvflags = [False] * burst
    recvdata = [0] * burst
    i = 0
    data = b''
    while sum(recvflags) != burst:
        while i < burst:
            if not recvflags[i]:
                sio.write(read_word(begin + 4 * i, i + offset + 1))
            i += 1
            size = sio.in_waiting
            if size  > 0:
                data += sio.read(size)
        i = 0

    return b''.join(recvdata)

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
