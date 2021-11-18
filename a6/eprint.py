import sys

def eprint(*args, **kwargs):
    """ print to stderr

    This function takes its arguments just as if it were the normal
    print function and instead prints to stderr.

    @param args: the arguments to print
    @param kwargs: the keyword arguments to print

    """

    print(*args, file=sys.stderr, **kwargs)
