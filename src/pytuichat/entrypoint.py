import sys

from .cli import runcli
from .tui import runtui
from .inbox import Inbox

def run():
    args = sys.argv[1:]

    if "--tui" in args:
        runtui()
    elif "--runInbox" in args:
        Inbox.runInbox()
    else:
        runcli(args)

if __name__ == "__main__":
    run()