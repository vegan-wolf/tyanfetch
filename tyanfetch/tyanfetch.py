#!/usr/bin/env python3

import platform
import os
import psutil
import random
import subprocess
import datetime
import sys
import re


COLORS = {
    "red": "\033[1;31m",
    "green": "\033[1;32m",
    "yellow": "\033[1;33m",
    "purple": "\033[1;34m",
    "blue": "\033[1;35m",
    "cyan": "\033[1;36m",
    "white": "\033[1;37m",
}
RESET = "\033[0m"
DEFAULT_COLOR = "cyan"


def get_accent_color():

    if len(sys.argv) > 1:
        requested_color = sys.argv[1].lower()
        if requested_color in COLORS:
            return COLORS[requested_color]
        else:
            print(f"Предупреждение: Цвет '{requested_color}' не поддерживается. Ипользую {DEFAULT_COLOR}.")
            print(f"Доступные цвета: {', '.join(COLORS.keys())}\n")

    return COLORS[DEFAULT_COLOR]


COLOUR = get_accent_color()
WHITE = "\033[1;37m"
RESET = "\033[0m"


def get_uptime():
    with open("/proc/uptime") as f:
        inp = [float(i) for i in f.read().split()]

    upt = datetime.timedelta(seconds=inp[0])
    days = upt.days
    hours, rem = divmod(int(upt.seconds), 3600)
    minutes, seconds = divmod(rem, 60)
    return f'{days} days, {hours} hours, {minutes} minutes, {seconds} seconds'


def get_os_name():
    try:
        os_info = platform.freedesktop_os_release()
        return f'{os_info.get('PRETTY_NAME', platform.system())} {os.uname().machine}'
    except AttributeError:
        return f"{platform.system()} {platform.release()}"


def get_cpu_model():
    if platform.system() == "Windows":
        return platform.processor()
    elif platform.system() == "Darwin":
        return os.popen("sysctl -n machdep.cpu.brand_string").read().strip()
    elif platform.system() == "Linux":
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":")[1].strip()
        except Exception:
            pass
    return "Unknown CPU"


def get_package_count():
    try:
        distro = platform.freedesktop_os_release().get("ID", "linux")

        if distro in ["arch", "manjaro", "endeavouros"]:
            p1 = subprocess.Popen(["pacman", "-Q"], stdout=subprocess.PIPE, text=True)
            count = len(p1.communicate()[0].splitlines())
            return f"{count} (pacman)"

        elif distro in ["ubuntu", "debian", "mint"]:
            output = subprocess.check_output(
                "dpkg-query -W -f='${db:Status-Abbrev}\\n'",
                shell=True, text=True
            )
            count = sum(1 for line in output.splitlines() if line.startswith("ii"))
            return f"{count} (dpkg)"

        elif distro == "fedora":
            p1 = subprocess.Popen(["rpm", "-qa"], stdout=subprocess.PIPE, text=True)
            count = len(p1.communicate()[0].splitlines())
            return f"{count} (rpm)"

    except Exception:
        pass
    return "Unknown"


def rounded_box(info, padding=1):
    pattern = re.compile(r'\x1b\[[0-9;]*m')
    true_length = [len(pattern.sub('', line)) for line in info]
    width = max(true_length) + padding*2

    TOP_LEFT, TOP_RIGHT = "╭", "╮"
    BOTTOM_LEFT, BOTTOM_RIGHT = "╰", "╯"
    HORIZ, VERT = "─", "│"

    top = f"{COLOUR}{TOP_LEFT}{HORIZ*width}{TOP_RIGHT}{RESET}"
    bottom = f"{COLOUR}{BOTTOM_LEFT}{HORIZ*width}{BOTTOM_RIGHT}{RESET}"

    result = [top]
    for line, vlen in zip(info, true_length):
        space = max(true_length) - vlen
        nw_info = " "*padding + line + " "*space  +" "*padding
        result.append(f"{COLOUR}{VERT}{RESET}{nw_info}{COLOUR}{VERT}{RESET}")

    result.append(bottom)
    return result


def find_info():
    user = os.environ.get('USER') or os.environ.get('USERNAME') or 'root'
    name_comp = platform.node()

    kernel_type = platform.system()
    kernel_release = platform.release()
    os_name = get_os_name()
    uptime = get_uptime()

    packages = get_package_count()

    mem = psutil.virtual_memory()
    mem_used = int(mem.used / 1024 / 1024)
    mem_total = int(mem.total / 1024 / 1024)

    terminal_name = os.environ.get('TERM') or 'xterm'

    base_colors = range(40, 48)
    bright_colors = range(100, 108)
    block = '   '
    row1 = ''
    for i in base_colors:
        row1 += f'\033[{i}m{block}'
    row1 += RESET
    row2 = ''
    for i in bright_colors:
        row2 += f'\033[{i}m{block}'
    row2 += RESET

    info_lines = [
        f"{COLOUR}{user}@{name_comp}{RESET}",
        f"{COLOUR}" + "-" * (len(user) + len(name_comp) + 1) + f"{RESET}",
        f"{COLOUR}OS:{RESET}       {os_name}",
        f"{COLOUR}Kernel:{RESET}   {kernel_type} {kernel_release}",
        f"{COLOUR}CPU:{RESET}      {get_cpu_model()}",
        # f"{CYAN}GPU:{RESET}     {get_gpu_model()}",
        f"{COLOUR}Uptime:{RESET}   {uptime}",
        f"{COLOUR}Packages:{RESET} {packages}",
        f"{COLOUR}Terminal:{RESET} {terminal_name}",
        f"{COLOUR}Memory:{RESET}   {mem_used} MiB / {mem_total} MiB",
        '',
        row1,
        row2,
    ]

    result = rounded_box(info_lines)
    return result

def write_info(distro_logo_file):
    distro_logo = []
    with open(distro_logo_file, "r", encoding='utf-8') as f:
        for line in f:
            clean_line = line.strip('\n').strip('\n')
            distro_logo.append(f"{COLOUR}{clean_line}{RESET}")
    pattern = re.compile(r'\x1b\[[0-9;]*m')
    true_length = [len(pattern.sub('', line)) for line in distro_logo]

    max_hor_len = max(true_length)
    info = find_info()
    max_vert_len = max(len(distro_logo), len(info))

    for i in range(max_vert_len):
        logo_part = distro_logo[i] if i < len(distro_logo) else ' '*max_hor_len
        info_part = info[i] if i < len(info) else ''
        print(f'{logo_part}    {info_part}')

def cli():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    num_distro_pic = os.path.join(script_dir, f'pics/pic{random.randint(1, 22)}.txt')

    write_info(num_distro_pic)

if __name__ == '__main__':
    cli()
