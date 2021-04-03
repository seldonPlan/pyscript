#!/usr/bin/env python3

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


# sanity checks
def version_check():
    """validate calling python is at least python 3.6"""
    if not (sys.version_info.major == 3 and sys.version_info.minor >= 6):
        v = sys.version_info
        version = f"{v.major}.{v.minor}.{v.micro}"
        print(f"ERROR: pyscriptenv init requires python>=3.6, detected {version}")
        sys.exit(1)


def cookiecutter_check():
    """validate cookiecutter command is available"""
    if shutil.which("cookiecutter") is None:
        print("ERROR: cookiecutter not found, please install then try again")
        sys.exit(1)


version_check()
cookiecutter_check()

parser = argparse.ArgumentParser(prog="pyscript-template")
parser.add_argument("name", help="pyscript application name")
parser.add_argument(
    "--path",
    action="store",
    type=str,
    default=".",
    help="path to install new pyscript application template",
)
parser.add_argument(
    "--config", action="store", type=str, help="template configuration file"
)
args = parser.parse_args()

_tmpl_config = None
if args.config is not None:
    _tmpl_config = Path(args.config).expanduser().resolve()
    if not _tmpl_config.exists():
        print(f"ERROR: template config file not found {str(_tmpl_config)}")

config = dict(
    name=args.name,
    install_path=Path(args.path).expanduser().resolve(),
    tmpl_config=_tmpl_config,
    tmpl=(Path(__file__) / ".." / "template").resolve(),
)

cmd = ["cookiecutter"]

if config["tmpl_config"] is not None:
    cmd.append("--config-file")
    cmd.append(str(config["tmpl_config"]))

cmd.append("--no-input")
cmd.append("--output-dir")
cmd.append(str(config["install_path"]))
cmd.append(str(config["tmpl"]))
cmd.append(f"project_name={config['name']}")

subprocess.run(cmd)
