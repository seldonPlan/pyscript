import re
import shutil
import sys
from pathlib import Path

print("pre_gen_project script...")

MODULE_REGEX = r"^[_a-zA-Z][_a-zA-Z0-9]+$"
module_name = "{{ cookiecutter.project_module }}"
if not re.match(MODULE_REGEX, module_name):
    print(f'ERROR: "{module_name}" is not a valid python module name')
    sys.exit(1)

if "{{ cookiecutter.install_vscode_project }}" == "yes":

    if shutil.which("grep") is None:
        print(
            "WARNING: grep command not found, bump version tasks defined in "
            ".vscode/tasks.json may not work properly"
        )

    paths = [
        (
            "vscode_pythonPath",
            Path("{{ cookiecutter.vscode_pythonPath }}".replace("${env:HOME}", "~")),
        ),
        (
            "vscode_buildPythonPath",
            Path(
                "{{ cookiecutter.vscode_buildPythonPath }}".replace("${env:HOME}", "~")
            ),
        ),
        (
            "vscode_blackPath",
            Path("{{ cookiecutter.vscode_blackPath }}".replace("${env:HOME}", "~")),
        ),
        (
            "vscode_flake8Path",
            Path("{{ cookiecutter.vscode_flake8Path }}".replace("${env:HOME}", "~")),
        ),
        (
            "vscode_mypyPath",
            Path("{{ cookiecutter.vscode_mypyPath }}".replace("${env:HOME}", "~")),
        ),
        (
            "vscode_isortPath",
            Path("{{ cookiecutter.vscode_isortPath }}".replace("${env:HOME}", "~")),
        ),
        (
            "vscode_bumpversion",
            Path("{{ cookiecutter.vscode_bumpversion }}".replace("${env:HOME}", "~")),
        ),
    ]

    for path in paths:
        if not path[1].expanduser().resolve().exists():
            print(f"WARNING: unable to verify path for {path[0]}")
