import sys

from cli import runcli
from tui import runtui

if __name__ == "__main__":
    args = sys.argv[1:]

    if "--tui" in args:
        runtui()
    else:
        runcli(args)