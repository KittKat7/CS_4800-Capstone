import sys

from pytuichat.cli import runcli
from pytuichat.tui import runtui
from pytuichat.inbox import Inbox

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