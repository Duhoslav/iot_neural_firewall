# -*- coding: utf-8 -*-
import sys
from sender_model import Sender


def parse_args(argv, expected):
    help_text = """
                ***********************
             Wrong arguments! \n 
             Type '--illegal' for illegal traffic simulation \n
             Specify ticks count (default=5)
                ***********************
             """
    err = 0
    if len(argv) > 2:
        err = 1
    else:
        if "--illegal" in argv:
            expected["--illegal"] = True
            argv.remove("--illegal")
        if len(argv) > 0:
            try:
                expected["ticks"] = int(argv[0])
                del argv[0]
            except:
                err = 1
        if len(argv) > 0:
            err = 1
    if err != 0:
        print(help_text)
        exit(1)
    # return expected


if __name__ == '__main__':
    expected = {
        "--illegal": False,
        "ticks": 5
    }
    if len(sys.argv) > 1:
        parse_args(sys.argv[1:], expected)
    remote = Sender(0, 10, 0)
    ticks = expected["ticks"]
    while ticks:
        res = remote.send_legal((not expected["--illegal"]))
        print(res)
        ticks -= 1
    remote.send_disconnect()
    exit(2)
