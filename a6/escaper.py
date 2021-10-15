def escaper(msg):
    """ escape message

    this function escapes special characters in the message.  These
    are 0x5c, 0x11 and 0x13 which are '\' and XON and XOFF characters.

    """

    out = bytes(sum([[0x5c, 0xFF ^ x ] if x in [0x11, 0x13, 0x5c] else [x] for x in msg], []))
    return out

def unescaper(msg):
    """ unescape message

    this function undoes any escape sequences in a received message
    """

    out = []
    escape = False
    for x in msg:
        if x == 0x5c:
            escape = True
            continue
        if escape:
            x = 0x5c ^ x ^ 0xa3
            escape = False
        out.append(x)
    return bytes(out)
