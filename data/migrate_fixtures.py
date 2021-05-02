#!/usr/bin/python3
"""Migrates"""

import argparse
import os
import platform
import re
import subprocess
import sys
from os.path import abspath, dirname, join, relpath

DEFAULT_DIR = relpath(join(dirname(__file__), "fixtures/"))
MANAGE_PY = relpath(join(dirname(dirname((abspath(join(__file__))))), join("tabbycat", "manage.py")))

# Arguments
parser = argparse.ArgumentParser(description="Migrates all fixtures in a directory. "
    "It's best to run this on a completely brand-new, unmigrated database.")

parser.add_argument("old_commit", type=str,
    help="Git commit (or branch name, etc.) before the migration")
parser.add_argument("new_commit", type=str,
    help="Git commit (or branch name, etc.) after the migration")
parser.add_argument("--dry-run", action="store_true", default=False,
    help="Print commands, don't run them.")
parser.add_argument("--directory", type=str, default=DEFAULT_DIR,
    help="Directory where fixtures are located, default: " + DEFAULT_DIR)
parser.add_argument("--unmigrate", type=str, default=[], nargs="+", metavar="APP/MIGRATION",
    help="App labels and migrations to use when unmigrating. These get passed "
    "to 'python manage.py migrate' when rolling back the migration, in "
    "preparation for the next fixture. Use the format: app_label/migration_name. "
    "For example: --unmigrate adjallocation/0008 participants/0037 actionlog/0019")

args = parser.parse_args()

if platform.system() == "Windows":
    subprocess_kwargs = dict(shell=True)
    use_color = False
else:
    subprocess_kwargs = dict()
    use_color = True


def print_command(command):
    message = "$ " + " ".join(command)
    if use_color:
        message = "\033[1;36m" + message + "\033[0m"
    print(message)


def run_command(command):
    print_command(command)
    if not args.dry_run:
        subprocess.check_call(command, **subprocess_kwargs)


def get_output_from_command(command):
    print_command(command)
    if args.dry_run:
        return ""
    output = subprocess.check_output(command, **subprocess_kwargs)
    output = output.decode()
    sys.stdout.write(output)
    sys.stdout.flush()
    return output


def print_yellow(message):
    if use_color:
        message = "\033[1;33m" + message + "\033[0m"
    print(message)


if args.unmigrate:
    unmigrations = [tuple(spec.split("/")) for spec in args.unmigrate]
    run_command(["git", "checkout", args.new_commit])
else:
    print_yellow("Figuring out what the migration difference is...")
    run_command(["git", "checkout", args.old_commit])
    run_command(["python", MANAGE_PY, "migrate", "--no-input"])
    run_command(["git", "checkout", args.new_commit])
    output = get_output_from_command(["python", MANAGE_PY, "migrate", "--no-input"])

    # The unmigration step should migrate to the one before the earliest
    # migation in the difference for each app. Most of the time, this will just
    # be the number one less than the earliest one, so we'll just run with that.
    # Where that's not the case, the user can use the --unmigrate option.
    matches = re.findall(r"\s+Applying (\w+)\.(\d+)_.+\.\.\.", output)
    migration_by_app = {}
    for app_label, migration_number in matches:
        existing = migration_by_app.setdefault(app_label, int(migration_number))
        if int(migration_number) - 1 < existing:
            migration_by_app[app_label] = int(migration_number) - 1
    unmigrations = [(app_label, "%04d" % (migration_number,)) for
            app_label, migration_number in migration_by_app.items()]

print_yellow("Unmigration specs:\n" + "\n".join("    %s %s" % spec for spec in unmigrations))

fixtures = os.listdir(args.directory)

for fixture in fixtures:
    path = join(args.directory, fixture)
    print_yellow("Migrating fixture %s..." % (path,))

    for app_label, migration_number in unmigrations:
        run_command(["python", MANAGE_PY, "migrate", app_label, migration_number, "--no-input"])

    run_command(["git", "checkout", args.old_commit])

    run_command(["python", MANAGE_PY, "flush", "--no-input"])
    run_command(["python", MANAGE_PY, "loaddata", path])

    run_command(["git", "checkout", args.new_commit])
    run_command(["python", MANAGE_PY, "migrate", "--no-input"])
    run_command(["python", MANAGE_PY, "checkpreferences"])
    run_command(["python", MANAGE_PY, "dumpdata", "--natural-foreign", "--natural-primary",
            "-e=availability", "-e=contenttypes", "-e=options", "-e=auth.Permission",
            "-e=admin.logentry", "-e=actionlog.actionlogentry", "-e=sessions", "-e=authtoken.token",
            "--indent=4", "--format=json", "--output=" + path])

print_yellow("Migrated %d fixtures." % len(fixtures))
