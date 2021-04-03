#!/usr/bin/env python3

"""
command line tool to initialize or update pyscript environments

requirements:
 - python >= 3.6
 - virtualenv, available on calling PATH

run `pyscript-init.py --help` for usage
run `pyscript-init.py --dry-run` to see what actions would be run by default
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

# environment dependency defaults
primary_reqs_default = [
    "click==7.1.2",
    "colorama==0.4.4",
    "requests==2.25.1",
]
build_reqs_default = [
    "build==0.3.1",
    "flit-core==3.2.0",
]


# sanity checks
def version_check():
    """validate calling python is at least python 3.6"""
    if not (sys.version_info.major == 3 and sys.version_info.minor >= 6):
        v = sys.version_info
        version = f"{v.major}.{v.minor}.{v.micro}"
        print(f"ERROR: pyscriptenv init requires python>=3.6, detected {version}")
        sys.exit(1)


def virtualenv_check():
    """validate virtualenv command is available"""
    if shutil.which("virtualenv") is None:
        print("ERROR: virtualenv not found, please install virtualenv, then try again")
        sys.exit(1)


def path_check(*args: Path):
    for path in args:
        if path.exists() and not path.is_dir():
            print(f"ERROR: path is not a directory [{str(path)}], will not overwrite")
            sys.exit(1)


# arg parsing
parser = argparse.ArgumentParser(prog="pyscript-init")
parser.add_argument(
    "--dry-run",
    action="store_true",
    help="show actions and exit",
)
parser.add_argument(
    "--force",
    action="store_true",
    default=False,
    help="force clearing of [primary, build] env directory first",
)
parser.add_argument(
    "--primary-name",
    action="store",
    type=str,
    metavar="NAME",
    default="pyscriptenv",
    help=argparse.SUPPRESS,
    # help="[primary] env directory name (default: pyscriptenv)",
)
parser.add_argument(
    "--primary-reqs",
    metavar="FILE",
    type=argparse.FileType(mode="r", encoding="UTF-8"),
    help=f"[primary] env requirements file (default: {','.join(primary_reqs_default)})",
)
parser.add_argument(
    "--primary-skip",
    action="store_true",
    help="[primary] env skip actions",
)
parser.add_argument(
    "--build-name",
    action="store",
    type=str,
    metavar="NAME",
    default="pyscriptbuild",
    help=argparse.SUPPRESS,
    # help="[build] env directory name (default: pyscriptbuild)",
)
parser.add_argument(
    "--build-reqs",
    metavar="FILE",
    type=argparse.FileType(mode="r", encoding="UTF-8"),
    help=f"[build] env requirements file\n(default: {','.join(build_reqs_default)})",
)
parser.add_argument(
    "--build-skip",
    action="store_true",
    help="[build] env skip actions",
)
parser.add_argument(
    "root",
    metavar="PYSCRIPT_ROOT_DIR",
    default="~/bin",
    nargs="?",
    help="directory [primary, build] envs will be installed into (default: ~/bin)",
)


# config processing
def normalize_config(ns: argparse.Namespace):
    root = Path(ns.root).expanduser().resolve()
    primary_dir = (root / ns.primary_name).resolve()
    build_dir = (root / ns.build_name).resolve()

    path_check(root, primary_dir, build_dir)

    primary_deps = (
        primary_reqs_default
        if ns.primary_reqs is None
        else [v.strip() for v in ns.primary_reqs.readlines()]
    )
    build_deps = (
        build_reqs_default
        if ns.build_reqs is None
        else [v.strip() for v in ns.build_reqs.readlines()]
    )

    return dict(
        root=root,
        force=ns.force,
        dry_run=ns.dry_run,
        envs=[
            dict(
                type="primary",
                name=ns.primary_name,
                dir=primary_dir,
                skip=ns.primary_skip,
                deps=primary_deps,
                force=ns.force,
            ),
            dict(
                type="build",
                name=ns.build_name,
                dir=build_dir,
                skip=ns.build_skip,
                deps=build_deps,
                force=ns.force,
            ),
        ],
    )


# actions
def virtualenv_cmd(path, force):
    cmd = [
        "virtualenv",
        "--python",
        sys.base_prefix + "/bin/python3",
        "--download",
        "--seeder",
        "pip",
        "--always-copy",
        "--no-setuptools",
        "--no-wheel",
        "--no-vcs-ignore",
    ]

    if force:
        cmd.append("--clear")

    cmd.append(path)

    return cmd


def pip_cmd(path, deps):
    cmd = [
        str(Path(path) / "bin" / "python3"),
        "-m",
        "pip",
        "install",
    ]

    cmd = cmd + deps
    return cmd


def main(config, dry_run):
    # header
    print("#" * 80)
    print(f"### {config['type'].upper()} - {config['name']} - {str(config['dir'])}")
    print("#" * 80, "\n")

    # show config on dry_run
    if dry_run:
        print(f"~~~ config {'[dry-run] ' if dry_run else ''}~~~")
        print(
            json.dumps(config, indent=4, sort_keys=True, default=lambda o: str(o)), "\n"
        )

    # virtualenv action
    cmd = virtualenv_cmd(config["dir"], config["force"])
    print(f"~~~ virtualenv command {'[dry-run] ' if dry_run else ''}~~~")
    print(" ".join([str(v) for v in cmd]), "\n")
    if not dry_run:
        subprocess.run(cmd)
    print()

    # pip action
    cmd = pip_cmd(config["dir"], config["deps"])
    print(f"~~~ pip command {'[dry-run] ' if dry_run else ''}~~~")
    print(" ".join(cmd), "\n")
    if not dry_run:
        subprocess.run(cmd)
    print()


# exit app when checks fail
version_check()
virtualenv_check()

# exit app on parse_arg fail
config = normalize_config(parser.parse_args())

# run for each configured env
for envconfig in config["envs"]:
    main(envconfig, config["dry_run"])
