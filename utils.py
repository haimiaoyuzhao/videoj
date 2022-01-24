import sys


def check_system():
    system = sys.platform.lower()
    if "darwin" in system:
        return "mac"
    elif "linux" in system:
        return "linux"
    elif "win" in system:
        return "windows"
    else:
        raise AttributeError()
