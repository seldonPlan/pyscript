#!/usr/bin/env python3

"""
simple pipx wrapper to maintain standard set of tools useful to pyscript envs and apps

NOTE: managing pipx installation is outside of the scope of this script
      see https://pipxproject.github.io/pipx/installation/ for more

requirements:
 - python >= 3.6
 - pipx, available on calling $PATH

run `pyscript-tools.py --help` for usage
"""

import argparse
import json
import shutil
import subprocess
import sys
from typing import Any, List

# pyscript development env tools
tools: List[Any] = [
    {
        "package": "virtualenv",
        "version": None,
        "category": "env_management",
        "required": True,
        "inject": [],
    },
    {
        "package": "black",
        "version": None,
        "category": "code_quality",
        "required": True,
        "inject": [],
    },
    {
        "package": "flake8",
        "version": None,
        "category": "code_quality",
        "required": True,
        "inject": ["flake8-bugbear"],
    },
    {
        "package": "isort",
        "version": None,
        "category": "code_quality",
        "required": True,
        "inject": [],
    },
    {
        "package": "mypy",
        "version": None,
        "category": "code_quality",
        "required": True,
        "inject": [],
    },
    {
        "package": "cookiecutter",
        "version": None,
        "category": "app_management",
        "required": True,
        "inject": [],
    },
    {
        "package": "bumpversion",
        "version": None,
        "category": "app_management",
        "required": True,
        "inject": [],
    },
    {
        "package": "pre-commit",
        "version": None,
        "category": "app_management",
        "required": True,
        "inject": [],
    },
]


# sanity checks
def version_check():
    """validate calling python is at least python 3.6"""
    if not (sys.version_info.major == 3 and sys.version_info.minor >= 6):
        v = sys.version_info
        version = f"{v.major}.{v.minor}.{v.micro}"
        print(f"ERROR: pyscriptenv init requires python>=3.6, detected {version}")
        sys.exit(1)


def pipx_check():
    """validate pipx command is available"""
    if shutil.which("pipx") is None:
        print("ERROR: pipx not found, please install pipx, then try again")
        sys.exit(1)


# arg parsing
parser = argparse.ArgumentParser(prog="pyscript-tools")
valid_ops = ["install", "list", "verify"]
parser.add_argument(
    "--dry-run",
    action="store_true",
    help="show actions and exit",
)
parser.add_argument(
    "--force",
    action="store_true",
    default=False,
    help="ensure tools are reinstalled",
)
parser.add_argument(
    "--category",
    metavar="CATEGORY",
    help="limit operations to tools of this category",
)
parser.add_argument(
    "--tool",
    metavar="PKG_NM",
    help="limit operations to named tool",
)
parser.add_argument(
    "op",
    help=f"operation to perform, must be one of [{','.join(valid_ops)}]",
)


# config processing
def normalize_config(ns: argparse.Namespace):
    _tools = tools
    if ns.category is not None:
        _tools = [t for t in tools if t["category"].lower() == ns.category]

    if ns.tool is not None:
        _tools = [t for t in _tools if t["package"].lower() == ns.tool]

    if ns.op.lower() not in valid_ops:
        print(
            f"ERROR: unrecognized operation [{ns.op}], "
            f"must be one of [{','.join(valid_ops)}]"
        )
        sys.exit(1)

    return dict(dry_run=ns.dry_run, force=ns.force, tools=_tools, op=ns.op.lower())


# actions
def install_cmd(tool, force):
    cmd = ["pipx", "install", "--include-deps"]

    if force:
        cmd.append("--force")

    cmd.append(
        f"{tool['package']}"
        f"{'' if tool['version'] is None else '==' + tool['version']}"
    )
    return cmd


def list_cmd():
    return ["pipx", "list", "--include-injected"]


def verify_cmd(tools):
    for tool in tools:
        which_result = shutil.which(tool["package"])
        print(
            f"[ { tool['package'] : <14} ] "
            f"{'NOT_FOUND' if which_result is None else which_result}"
        )


def main(config):
    # header
    print("#" * 80)
    print("### pyscript tool management")
    print("#" * 80, "\n")

    # show config on dry_run
    if config["dry_run"]:
        print(f"~~~ config {'[dry-run] ' if config['dry_run'] else ''}~~~")
        print(
            json.dumps(config, indent=4, sort_keys=True, default=lambda o: str(o)), "\n"
        )

    # virtualenv action
    if config["op"] == "verify":
        print(f"~~~ verify {'[dry-run] ' if config['dry_run'] else ''}~~~", "\n")
        print(f"[ { 'TOOL_NAME' : <14} ] TOOL_PATH")
        print("~" * 60)
        verify_cmd(config["tools"])
        return

    if config["op"] == "list":
        print(f"~~~ pipx list {'[dry-run] ' if config['dry_run'] else ''}~~~", "\n")
        cmd = list_cmd()
        print(" ".join([str(v) for v in cmd]), "\n")
        if not config["dry_run"]:
            subprocess.run(cmd)
        return

    if config["op"] == "install":
        print(f"~~~ pipx install {'[dry-run] ' if config['dry_run'] else ''}~~~")
        for tool in config["tools"]:
            cmd = install_cmd(tool, config["force"])
            print(" ".join([str(v) for v in cmd]), "\n")
            if not config["dry_run"]:
                subprocess.run(cmd)
            print()
        return


# exit app when checks fail
version_check()
pipx_check()

# exit app on parse_arg fail
config = normalize_config(parser.parse_args())

main(config)
