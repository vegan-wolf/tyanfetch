import platform
import os
import psutil
import random
import subprocess

colour_code = 36
COLOUR = f"\033[1;{colour_code}m"
WHITE = "\033[1;37m"
RESET = "\033[0m"


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


def find_info():
    user = os.environ.get('USER') or os.environ.get('USERNAME') or 'root'
    name_comp = platform.node()

    kernel_type = platform.system()
    kernel_release = platform.release()
    os_name = get_os_name()
    uptime = psutil.boot_time()

    packeges = get_package_count()

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
        f"{COLOUR}{user}{WHITE}@{COLOUR}{name_comp}{RESET}",
        f"{WHITE}" + "-" * (len(user) + len(name_comp) + 1) + f"{RESET}",
        f"{COLOUR}OS:{RESET}      {os_name}",
        f"{COLOUR}Kernel:{RESET}  {kernel_type} {kernel_release}",
        f"{COLOUR}CPU:{RESET}     {get_cpu_model()}",
        # f"{CYAN}GPU:{RESET}    {get_gpu_model()}",
        f"{COLOUR}Uptime:{RESET}  {uptime}",
        f"{COLOUR}Packages:{RESET}    {packeges}",
        f"{COLOUR}Terminal:{RESET}    {terminal_name}",
        f"{COLOUR}Memory:{RESET}  {mem_used} MiB / {mem_total} MiB",
        '',
        row1,
        row2,
    ]

    return info_lines

def write_info(distro_logo_file):
    distro_logo = []
    with open(distro_logo_file, "r", encoding='utf-8') as f:
        for line in f:
            clean_line = line.strip('\n').strip('\n')
            distro_logo.append(clean_line)
    max_hor_len = max(len(line) for line in distro_logo)
    info = find_info()
    max_vert_len = max(len(distro_logo), len(info))

    for i in range(max_vert_len):
        logo_part = distro_logo[i] if i < len(distro_logo) else ''
        info_part = info[i] if i < len(info) else ''
        print(f'{logo_part}    {info_part}')


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    num_distro_pic = os.path.join(script_dir, f'pics/pic{random.randint(1, 22)}.txt')

    write_info(num_distro_pic)



if __name__ == '__main__':
    main()
