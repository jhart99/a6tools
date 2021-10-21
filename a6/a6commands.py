from .rdadebug import write_register_int8
from .rdadebug import read_register_int8
from .rdadebug import write_block
from .rdadebug import compute_check

def h2p_command(msg):
    """ Format a frame for an h2p command

    The CPS software sends commands to a special debug register
    00000005.  Writing a value to this register throws an interupt
    which is picked up by a function on the device.

    0x00 : Command finished, clears semaphore
    0xA5 : Process command with RxByHostPortCB
    0xEE : Reboot
    0xFF : Handle with boot_HstCmdBasicHandler

    """
    return write_register_int8(0x5, msg)

def set_uart_to_normal():
    """ Set device uart to host mode

    The CPS software sends repeated requests to set internal register
    00000003 to 0x80 which has the effect of locking the UART to debug
    mode

    """
    return write_register_int8(3, 0x00)

def set_uart_to_host():
    """ Set device uart to host mode

    The CPS software sends repeated requests to set internal register
    00000003 to 0x80 which has the effect of locking the UART to debug
    mode

    """
    return write_register_int8(3, 0x80)

def reboot_and_freeze():
    """ Reboot and freeze the processor

    This command comes from coolwatcher and resets the processor and
    immediately halts it.  This is useful for stepping through the
    boot process, but also allows some areas of ROM to be read without
    crashing

    """
    return write_register_int8(0, 0x03)

def read_uart_to_host():
    """ make a frame containing a knock command

    this function creates a frame that I assume wakes up the device
    for further commands.

    """
    return read_register_int8(3)

def ate_command(cmd, p_atecps_write):
    """ make a frame containing a knock command

    this function creates a frame that I assume wakes up the device
    for further commands.

    """
    cmd = bytearray(cmd, 'utf-8') + b'\r'
    cmd += bytes(4 - len(cmd) % 4)
    return write_block(p_atecps_write, cmd)

def cps_command(cmd, p_atecps_write):
    """ make a frame containing a knock command

    this function creates a frame that I assume wakes up the device
    for further commands.

    """
    length = (len(cmd) + 4).to_bytes(1, 'big')
    check = compute_check(length + cmd)
    begin = bytes([0xaa])
    end = bytes([0xbb])
    msg = begin + length + cmd + check + end
    padding = 4 - (len(msg) % 4)
    return write_block(p_atecps_write, msg + bytes([0x00]) * padding)
