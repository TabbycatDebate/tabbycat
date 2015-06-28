import subprocess
import platform

if platform.system() == "Windows":
    subprocess_kwargs = dict(shell=True)
    use_color = False
else:
    subprocess_kwargs = dict()
    use_color = True

def print_command(command):
    message = " $ " + " ".join(command)
    if use_color:
        message = "\033[0;36m" + message + "\033[0m"
    print message

def run_command(command):
    print_command(command)
    subprocess.check_call(command, **subprocess_kwargs)

run_command(["python", "manage.py", "makemigrations", "debate"])
run_command(["python", "manage.py", "migrate"])