import os
import time
import getpass
import argparse


USERNAME = getpass.getuser()
# EXPANSION_LEVEL = "Rebirth"
# EXPANSION_LEVEL = "Afterbirth"
# EXPANSION_LEVEL = "Afterbirth+"
EXPANSION_LEVEL = "Repentance"


# From: https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal
class BColors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    PINK = "\033[38;5;206m"


log_file_handle = None
cached_length = 0


def main():
    parser = argparse.ArgumentParser(description="Log viewer for The Binding of Isaac.")
    parser.add_argument(
        "-f",
        dest="LOG_FILE_PATH",
        default=f"C:\\Users\\{USERNAME}\\Documents\\My Games\\Binding of Isaac {EXPANSION_LEVEL}\\log.txt",
        type=str,
        help="custom filepath to TBoI log file.\nby default 'C:\\Users\\{USER}\\Documents\\My Games\\Binding of Isaac {EXPANSION}\\log.txt'",
    )
    parser.add_argument(
        "-t",
        "--tail",
        type=int,
        required=False,
        help="show last N of log lines",
        default=0,
    )
    parser.add_argument(
        "-g",
        dest="grep",
        default=None,
        type=str,
        help="print lines only with selected string",
        required=False,
    )
    parser.add_argument(
        "-s",
        dest="highlight",
        default=None,
        type=str,
        help="highlights lines containing this string",
        required=False,
    )
    args = parser.parse_args()

    while True:
        file_size = os.path.getsize(args.LOG_FILE_PATH)
        if has_log_changed(file_size):
            read_log(file_size, args)
        time.sleep(0.1)


def has_log_changed(file_size: int):
    return file_size != cached_length


def read_log(file_size: int, args: argparse.Namespace):
    global log_file_handle
    global cached_length

    if log_file_handle is None or cached_length > file_size:
        # This is a new log file
        log_file_handle = open(args.LOG_FILE_PATH, "rb")
    elif cached_length < file_size:
        # Append existing content
        log_file_handle.seek(cached_length)

    cached_length = file_size
    new_log_content = log_file_handle.read()
    parse_log(new_log_content, args)


def parse_log(log_content: str, args: argparse.Namespace):
    log_lines = log_content.splitlines()
    tail = len(log_lines)
    if args.tail:
        tail = args.tail

    for line in log_lines[-tail:]:
        parse_log_line(line, args.grep, args.highlight)


def parse_log_line(line_bytes: str, grep: str, highlight: str):
    # We read the log in binary form, so we need to convert it to a normal string
    line = line_bytes.decode("Latin-1").strip()

    # Don't parse empty lines
    if line == "":
        return

    lowercase_line = line.lower()

    # Don't print some specific messages
    if lowercase_line.startswith("[info] - [warn] sound") and lowercase_line.endswith(
        "has no samples."
    ):
        return
    if lowercase_line.startswith("[info] - lua mem usage: "):
        return
    if (
        lowercase_line
        == "[info] - [warn] steamcloud is either not available or disabled in options.ini."
    ):
        return
    if lowercase_line.startswith("[info] - [warn] no animation named "):
        return
    if lowercase_line.startswith(
        "[info] - [warn] last boss died without triggering the deathspawn."
    ):
        return
    if lowercase_line.startswith("[info] - [warn] item pool ran out of repicks"):
        return
    if lowercase_line.startswith("[assert] - error: game start seed was not set."):
        return
    if lowercase_line.startswith("[assert] - entity teleport detected!"):
        return
    if grep is not None and grep.lower() not in lowercase_line:
        return

    if (
        "error" in lowercase_line
        or "failed" in lowercase_line
        or " err: " in lowercase_line
    ):
        # Print all errors
        print_color(line, BColors.FAIL)
    elif "warn" in lowercase_line:
        # Print all warnings
        print_color(line, BColors.WARNING)
    elif highlight and highlight.lower() in lowercase_line:
        # custom highlight
        print_color(line, BColors.OKBLUE)
    elif "Compilation successful." in line:
        # Print IsaacScript success messages in green
        print_color(line, BColors.OKGREEN)
    elif "MC_POST_GAME_STARTED" in line or "Connected to localhost" in line:
        print_color(line, BColors.OKCYAN)
    elif "getting here" in lowercase_line:
        print_color(line, BColors.PINK)
    elif "lua" in lowercase_line:
        # Print lines that have to do with Lua
        print_color(line)
    elif not lowercase_line.startswith("[info]"):
        # Print multi-line Lua log output
        print_color(line)


def print_color(msg: str, color: str = ""):
    if color != "":
        msg = f"{color}{msg}{BColors.ENDC}"

    # Sometimes, printing can fail due to TMTRAINER collectibles.
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        print("[Unable to print line due to corrupted characters.]")


if __name__ == "__main__":
    main()
