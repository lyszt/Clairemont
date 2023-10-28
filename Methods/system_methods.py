import datetime


def console_log(message, err=None):
    print(f"[{datetime.datetime.now()}] [INFO    ] {message}")
    if err:
        print(err)