from .rdadebug import write_register_int8
from .rdadebug import read_register_int8
from .rdadebug import write_block
from .rdadebug import compute_check
from .eprint import eprint

def h2p_command(msg):
    """ Format a frame for an h2p command

    The CPS software sends commands to a special debug register
    00000005.  Writing a value to this register throws an interupt
    which is picked up by a function on the device.

    0x00 : Command finished, clears semaphore
    0xA5 : Process command with RxByHostPortCB
    0xEE : Reboot
    0xFF : Handle with boot_HstCmdBasicHandler

    @param msg: the message to send
    @return: the frame to send

    """
    return write_register_int8(0x5, msg)

def set_uart_to_normal():
    """ Set device uart to host mode

    The CPS software sends repeated requests to set internal register
    00000003 to 0x80 which has the effect of locking the UART to debug
    mode

    @return: the frame to send

    """
    return write_register_int8(3, 0x00)

def set_uart_to_host():
    """ Set device uart to host mode

    The CPS software sends repeated requests to set internal register
    00000003 to 0x80 which has the effect of locking the UART to debug
    mode

    @return: the frame to send

    """
    return write_register_int8(3, 0x80)

def reboot_and_freeze():
    """ Reboot and freeze the processor

    This command comes from coolwatcher and resets the processor and
    immediately halts it.  This is useful for stepping through the
    boot process, but also allows some areas of ROM to be read without
    crashing

    @return: the frame to send

    """
    return write_register_int8(0, 0x03)

def read_uart_to_host():
    """ make a frame containing a knock command

    this function creates a frame that I assume wakes up the device
    for further commands.

    @return: the frame to send

    """
    return read_register_int8(3)

def ate_command(ate_cps_addr, cmd):
    """ make a frame containing an ATE command

    @param cmd: the command to send
    @param p_atecps_write: the address of the CPS write register
    @return: the frame to send

    """
    cmd = bytearray(cmd, 'utf-8') + b'\r'
    cmd += bytes(4 - len(cmd) % 4)
    return write_block(ate_cps_addr, cmd)

def cps_command(ate_cps_addr, cmd):
    """ make a frame containing an CPS command

    @param cmd: the command to send
    @param p_atecps_write: the address of the CPS write register
    @return: the frame to send

    """
    length = (len(cmd) + 4).to_bytes(1, 'big')
    check = compute_check(length + cmd)
    begin = bytes([0xaa])
    end = bytes([0xbb])
    msg = begin + length + cmd + check + end
    padding = 4 - (len(msg) % 4)
    return write_block(ate_cps_addr, msg + bytes([0x00]) * padding)

class CPSFrame:
    """ Received CPS class

    This class decodes CPS frames received from the device.
    """
    check_fail = False
    length = 0
    type = 0
    content = bytes([])
    def __init__(self, msg):
        eprint(msg.hex())
        if (msg[-1].to_bytes(1, 'big') != compute_check(msg[1:-2])):
            self.check_fail = True
            eprint('CPS frame check failed')
            return
        self.length = msg[1]
        self.type = int.from_bytes(msg[2:4], 'big')
        self.is_ok = msg[4] == 0x01
        self.content = msg[5:-3]
    def __repr__(self):
        return 'packet length {} type {} is_ok {} content {}'.format(self.length, self.type, self.is_ok, self.content)

class ChanInfoFrame(CPSFrame):
    """ Received ChanInfoFrame class

    This class decodes ChanInfoFrame frames received from the device.

    "\tcpsInst.chanInfo.nChanIndex=%d\n
     \tcpsInst.chanInfo.nChanType=%d\n
     \tcpsInst.chanInfo.nVox=%d\n
     \tcpsInst.chanInfo.nPower=%d\n
     \tcpsInst.chanInfo.nRxFreq=%d\n
     \tcpsInst.chanInfo.nTxFreq=%d\n
     \tcpsInst.chanInfo.nTxContactsIdx=0x%08x\n
     \tcpsInst.chanInfo.nColorCode=%d\n
     \tcpsInst.chanInfo.nTimeSlot=%d\n
     \tcpsInst.chanInfo.bPoliteCall=%d\n"
     \tcpsInst.chanInfo.nEmrSys=%d\n
     \tcpsInst.chanInfo.nEncry=%d\n 
     \tcpsInst.chanInfo.nTypeWideNarrow=%d\n 
     \tcpsInst.chanInfo.nRxCtdcs=%d\n 
     \tcpsInst.chanInfo.bRxCtdcsInvert=%d\n 
     \tcpsInst.chanInfo.bTxCtdcsInvert=%d\n 
     \tcpsInst.chanInfo.nTxCtdcs=%d\n 
     \tcpsInst.chanInfo.nRxGrpListIdx=%d\n"
    """
    def __init__(self, msg):
        super().__init__(msg)
        self.index = int.from_bytes(self.content[0:2], 'little')
        self.chantype = self.content[2]
        self.rxFreq = int.from_bytes(self.content[4:8], 'little')
        self.txFreq = int.from_bytes(self.content[8:12], 'little')
        self.txContactIndex = int.from_bytes(self.content[12:16], 'little')
        self.colorCode = self.content[16]
        self.timeslot = self.content[17]
        self.polite = self.content[18]
        self.emrSys = int.from_bytes(self.content[1:2], 'big')
        self.encryption = int.from_bytes(self.content[1:2], 'big')
        self.widenarrow = int.from_bytes(self.content[1:2], 'big')
        self.rxctdcs = int.from_bytes(self.content[1:2], 'big')
        self.rxctdcsinvert = int.from_bytes(self.content[1:2], 'big')
        self.txctdcsinvert = int.from_bytes(self.content[1:2], 'big')
        self.txctdcs = int.from_bytes(self.content[1:2], 'big')
        self.rxGroupIdx = int.from_bytes(self.content[1:2], 'big')
        self.vox = int.from_bytes(self.content[1:2], 'big')
    def __repr__(self):
        return 'packet length {} type {} is_ok {} index {} chantype {} rxfreq {} txfreq {}'.format(
            self.length, self.type, self.is_ok, self.index, self.chantype, self.rxFreq, self.txFreq)