import asyncio
import serial_asyncio

from .eprint import eprint
from .escaper import unescaper
from .rdadebug import compute_check
from .rdadebug import read_word, write_block, RdaFrame
from .a6commands import h2p_command, set_uart_to_host
from .a6commands import ate_command
from .a6commands import cps_command
import datetime
import functools

__author__ = "jhart99"
__license__ = "MIT"


class RdaDebugProtocol(asyncio.Protocol):
    """ Serial RDA debug protocol

    Sends and receives messages from the RDA debug port.  Messages to be sent
    are added to the write queue. And this class will pick up the messages and
    write them to the serial port.  Valid received messages are added to the
    read_queue.

    One issue with this protocol is that the messages are not necessarily
    returned in order and there can be significant latency between the message
    being sent and the message being received.

    
    """

    def __init__(self, read_queue, write_queue):
        """ Constructor

        """
        super().__init__()
        self.transport = None
        self.read_queue = read_queue
        self.write_queue = write_queue
        self.verbose = 0

    def connection_made(self, transport):
        """Store the serial transport and schedule the task to send data.
        """
        # eprint('CoolProtocol connection created')
        self.transport = transport
        # self.transport.set_write_buffer_limits(128, 16)
        self.buf = bytes()
        asyncio.ensure_future(self.send())

    def connection_lost(self, exc):
        """Connection closed
        Needed to set the future flag showing this thread is complete
        """
        # eprint('CoolProtocol connection lost')
        super().connection_lost(exc)

    def data_received(self, data):
        """Store received data and process buffer to look for frames

        if the current read block is finished. Set the complete
        semaphore if appropriate
        """
        # eprint(data.hex())
        data = unescaper(data)
        self.buf += data
        # eprint(self.buf.hex())
        self.process_buffer()

    def process_buffer(self):
        """ Process in the read buffer

        scans for ad begin words and discards defective packets automatically
        """
        if len(self.buf) > 4096:
            self.buf = bytes()
        begin = self.buf.find(0xad)
        while (begin >= 0):
            # eprint('begin msg')
            if len(self.buf) < begin + 3:
                # too short to read msg length, fragmented
                # eprint('too short to read msg length, fragmented')
                return
            msglen = int.from_bytes(self.buf[begin+1:begin+3], byteorder = 'big', signed = False)
            nextframe = begin + 4 + msglen
            if len(self.buf) < nextframe:
                # frame incomplete, fragmented
                # eprint('frame incomplete, fragmented')
                return
            frame = self.buf[begin:nextframe]
            # eprint(self.buf[begin:nextframe].hex())
            msg = frame[3:-1]
            # eprint(f'{msg.hex()} {compute_check(msg)} {frame[-1]}')
            if compute_check(msg) == frame[-1].to_bytes(1, 'big'):
                # only process the message if the check field matches
                asyncio.ensure_future(self.read_queue.put(frame))
            else:
                # eprint(f'bad check {msg.hex()} {compute_check(msg).hex()} {frame[-1]:x}')
                pass
            self.buf = self.buf[nextframe:]
            begin = self.buf.find(0xad)

    async def send(self):
        while True:
            msg = await self.write_queue.get()
            self.transport.write(msg)
            self.write_queue.task_done()
            # print(msg.hex())
            await asyncio.sleep(0)

class RdaDebugSerialInterface:
    def __init__(self, args):
        self.loop = asyncio.get_event_loop()
        self.read_queue = asyncio.Queue()
        self.write_queue = asyncio.Queue()
        debug_partial = functools.partial(RdaDebugProtocol, self.read_queue, self.write_queue)
        serial_connection = serial_asyncio.create_serial_connection(self.loop,
            debug_partial,
            args.port,
            args.baudrate,
            xonxoff=True)
        self.serial_connection = asyncio.create_task(serial_connection)
        self._ate_cps_addr = 0
        self._ate_cps_resp_addr = 0
        self._uart_resp_addr = 0
        self.verbose = args.verbose

    async def receive_async(self, reqlen):
        """ Receives a series of messages from the queue
        
        This function will wait for a message to be available in the queue.  If
        reqlen valid messages are read, it will return the results.
        @param q: the queue to read from
        @param reqlen: the number of messages to read
        @return: bytes of the payload of the messages.
        """
        
        data = []
        count = 1
        while count <= reqlen:
            msg = await self.read_queue.get()
            frame = RdaFrame(msg)
            if self.verbose > 1: print(f'{frame.seq:x} {count:x} {frame.content.hex()}')
            if frame.seq != 0:
                data.append(frame.content)
                count += 1
            else:
                # if seq = 0, then the frame contains an event
                if self.verbose >=1 : 
                    print(f'{datetime.datetime.now().isoformat()} event {int.from_bytes(frame.content, "little"):08x}')
            self.read_queue.task_done()
    
        return b''.join(data)

    async def read_range(self, begin, end, max_requests=0xf0):
        """ Read a range of memory
    
        Reads a range of memory and returns the data.  The range is inclusive.
    
        @param begin: begin address
        @param end: end address
        @return: value of the bytes read
    
        """
        cur = begin
        out = list()
        last_ping = datetime.datetime.now()
        while cur < end:
            requests = end - cur 
            if requests > max_requests * 4:
                requests = max_requests * 4
            begin_time = datetime.datetime.now()
            out.append(await self.read_block(cur, cur + requests))
            end_time = datetime.datetime.now()
            # await asyncio.sleep(0.06 - (end_time - begin_time).microseconds / 1000000)
            cur += requests
            if (end_time - last_ping).seconds > 4:
                if self.verbose: print('ping')
                last_ping = end_time
                await self.send_cps_command(bytes([0x0a, 0x05]))
        return b''.join(out)

    async def write_range(self, begin, data, block_size=0x80):
        """ Write a range of memory
    
        Writes a range of memory using given data
    
        @param begin: begin address
        @param data: data to write
    
        """
        cur = 0
        last_ping = datetime.datetime.now()
        end = len(data)
        while cur < end:
            bytes_to_write = end - cur 
            if bytes_to_write > block_size:
                bytes_to_write = block_size
            begin_time = datetime.datetime.now()
            await self.write_queue.put(write_block(begin + cur, data[cur:cur + bytes_to_write]))
            end_time = datetime.datetime.now()
            await asyncio.sleep(0.06 - (end_time - begin_time).microseconds / 1000000)
            if self.verbose >=1 : 
                print(f'{begin_time.isoformat()} {end_time.isoformat()} {begin + cur:08x} {bytes_to_write:x}')
            cur += bytes_to_write
            if (end_time - last_ping).seconds > 4:
                if self.verbose: print('ping')
                last_ping = end_time
                await self.send_cps_command(bytes([0x0a, 0x05]))

    
    async def read_block(self, begin, end):
        """ Read a block of memory
    
        Reads a block of memory and returns the data.  The block is inclusive.
        Cannot be larger than 0xfc reads
    
        @param begin: begin address
        @param end: end address
        @return: value of the bytes read
    
        """
        requests = (end - begin) // 4
        if requests > 0xffc:
            raise ValueError('Cannot read more than 0xfc bytes at a time')
        while True:
            begin_time = datetime.datetime.now()
            # start a receive task for the requests in this batch
            receive_complete = asyncio.create_task(self.receive_async(requests))
            # load up the write queue with the requests
            for i in range(requests):
                self.write_queue.put_nowait(read_word(begin + i * 4, (i % 0xfc) + 1))
                # why?  each read is 4 bytes.  The sequence number can be in the
                # range of 0x01-0xfe 0x00 will conflict with events and is a bad
                # idea.  0xff seems to have a special meaning and don't come back
                # ever.
            # flush the write queue before continuing
            await self.write_queue.join()
    
            try:
                # no reason to wait longer than 60ms
                await asyncio.wait_for(receive_complete, timeout=0.06)
                end_time = datetime.datetime.now()
                if self.verbose >=1 : 
                    print(f'{begin_time.isoformat()} {end_time.isoformat()} {begin:08x} {requests:x} {len(receive_complete.result()):x}')
                return receive_complete.result()
            except asyncio.TimeoutError:
                # if we have an error (not all requests were received) or timeout, we need to resend the requests
                end_time = datetime.datetime.now()
                if self.verbose >=1 : 
                    print(f'{begin_time.isoformat()} {end_time.isoformat()} timeout')

    async def write_flush_pause(self, msg, sleep = 0.07):
        """ Write out to serial and wait for the radio to process the command
    
        @param msg: bytes to write
        @param write_queue: the queue to write to
        @param sleep: time to sleep after writing in ms
    
        """
        self.write_queue.put_nowait(msg)
        await self.write_queue.join()
        await asyncio.sleep(sleep)
    
    async def send_ate_command(self, msg):
        """ Send a command to the ATE/CPS function on the radio
    
        To send a command to the ATE or CPS software on the radio, it has
        to be surrounded by these h2p commands which clear the registers
        and then throw and interupt which causes the command to be
        executed
        
        @param msg: bytes to write
    
        """
        await self.write_flush_pause(h2p_command(0))
        await self.write_flush_pause(ate_command(self.ate_cps_addr, msg))
        await self.write_flush_pause(h2p_command(0xa5))
    
    async def send_cps_command(self, msg):
        """ Send a command to the ATE/CPS function on the radio
    
        To send a command to the ATE or CPS software on the radio, it has
        to be surrounded by these h2p commands which clear the registers
        and then throw and interupt which causes the command to be
        executed
    
        @param msg: bytes to write
    
        """
        await self.write_flush_pause(h2p_command(0))
        await self.write_flush_pause(cps_command(self.ate_cps_addr, msg))
        await self.write_flush_pause(h2p_command(0xa5))

    async def init_preamble(self):
        """ Initialize the radio

        This is a reproduction of the commands sent by the official CPS software
        """
        for _ in range(12):
            await self.write_flush_pause(set_uart_to_host())
        await self.init_cps_interface()
        for _ in range(6):
            await self.send_cps_command(bytes([0x0a, 0x06]))
        await self.send_cps_command(bytes([0x0a, 0x08]))
        await self.send_cps_command(bytes([0x00, 0x2b, 0x00]))
        if self.verbose >=1: print('init done')

    async def finalizer(self):
        """ Finalize the radio

        This is a reproduction of the commands sent by the official CPS software
        """
        await self.send_cps_command(bytes([0x0a, 0x04]))
        await self.send_cps_command(bytes([0x0a, 0x05]))
        await self.send_cps_command(bytes([0x0a, 0x04]))
        await self.send_cps_command(bytes([0x0a, 0x04]))
        if self.verbose >=1: print('finalizer done')

    async def send_reboot_request(self):
        await self.write_flush_pause(h2p_command(0xee))

    async def init_cps_interface(self):
        """ Initialize the CPS interface
        
        The CPS interface is contained in the XCPU SRAM.  This function reads
        all of the values and loads them into the class for later use.
        
        """
        self._ate_cps_addr = await self.read_block(0x81c00270, 0x81c00274)
        self._ate_cps_addr = int.from_bytes(self._ate_cps_addr, byteorder='little')
        self._ate_cps_resp_addr = await self.read_block(0x81c00264, 0x81c00268)
        self._ate_cps_resp_addr = int.from_bytes(self._ate_cps_resp_addr, byteorder='little')
        self._ate_cps_struct_addr = await self.read_block(0x81c00268, 0x81c0026c)
        self._ate_cps_struct_addr = int.from_bytes(self._ate_cps_struct_addr, byteorder='little')
        self._cps_header_addr = await self.read_block(self._ate_cps_struct_addr, self._ate_cps_struct_addr + 0x04)
        self._cps_header_addr = int.from_bytes(self._cps_header_addr, byteorder='little')
        if self._cps_header_addr < 0x82000000 or self._cps_header_addr > 0x82400000:
            raise(ValueError('CPS header address is invalid'))
        self._cps_header_len = await self.read_block(self._ate_cps_struct_addr + 0x04, self._ate_cps_struct_addr + 0x08)
        self._cps_header_len = int.from_bytes(self._cps_header_len, byteorder='little')
        if self._cps_header_len < 0x0 or self._cps_header_len > 0xf00:
            raise(ValueError('CPS header len is invalid'))
        self._cps_body_addr = await self.read_block(self._ate_cps_struct_addr + 0x08, self._ate_cps_struct_addr + 0x0c)
        self._cps_body_addr = int.from_bytes(self._cps_body_addr, byteorder='little')
        if self._cps_body_addr < 0x82000000 or self._cps_body_addr > 0x82400000:
            raise(ValueError('CPS body address is invalid'))
        self._cps_body_len = await self.read_block(self._cps_header_addr + 0x14, self._cps_header_addr + 0x18)
        self._cps_body_len = int.from_bytes(self._cps_body_len, byteorder='little') - self._cps_header_len
        if self._cps_body_len < 0x0 or self._cps_body_len > 0xf0000:
            raise(ValueError('CPS body len is invalid'))
        self._uart_resp_addr = await self.read_block(0x81c0026c, 0x81c00270)
        self._uart_resp_addr = int.from_bytes(self._uart_resp_addr, byteorder='little')

    async def read_cps(self):
        """ Read the CPS from the radio
        
        @return: the CPS in bytes
        """
        # send the read specific commands to the CPS
        await self.send_cps_command(bytes([0x0a, 0x07]))
        await self.send_cps_command(bytes([0x0a, 0x03]))
        await self.send_cps_command(bytes([0x0a, 0x00]))
        # read the header and body and return the result
        header = await self.read_range(self._cps_header_addr, self._cps_header_addr + self._cps_header_len)
        body = await self.read_range(self._cps_body_addr, self._cps_body_addr + self._cps_body_len)
        return header + body

    async def write_cps(self, in_cps):
        """ Read the CPS from the radio
        
        @return: the CPS in bytes
        """
        # send the read specific commands to the CPS
        await self.send_cps_command(bytes([0x0a, 0x00]))
        await self.send_cps_command(bytes([0x0a, 0x01]))
        # write the header and body 
        await self.write_range(self._cps_header_addr, in_cps[0:self._cps_header_len])
        if self.verbose: print('wrote header')
        await self.write_range(self._cps_body_addr, in_cps[self._cps_header_len:])
        if self.verbose: print('wrote body')
        await self.send_cps_command(bytes([0x0a, 0x02]))

    async def atecps_resp_read(self):
        """ Read the response from an ATECPS command

        @return: response from ATECPS command
        """
        length = await self.read_block(self.ate_cps_resp_length_addr, self.ate_cps_resp_length_addr + 4)
        length = int.from_bytes(length, 'little')
        response = await self.read_block(self.ate_cps_resp_addr, self.ate_cps_resp_addr + length)
        return response

    async def uart_resp_read(self):
        """ Read the response from an ATECPS command that would be sent over UART

        @return: response from ATECPS command that would be sent to the UART
        """
        length = 0xff
        response = await self.read_block(self.uart_resp_addr, self.uart_resp_addr + length)
        return response

    @property
    def ate_cps_addr(self):
        """ return the address of the ate command
        """
        return self._ate_cps_addr

    @property
    def ate_cps_resp_addr(self):
        """ return the address of the ate command response
        """
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
        return self._uart_resp_addr

    