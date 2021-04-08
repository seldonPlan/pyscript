from pathlib import Path
from typing import Optional, Tuple, Union

import pytomlpp

from .default import DEFAULT_CONFIG

# fmt:off
DEFAULT_CONFIG_FILE = (
    Path("{{ cookiecutter.project_default_config_root }}") / "{{ cookiecutter.project_slug }}" / "{{ cookiecutter.project_default_config_file }}"  # noqa: E501
).expanduser().resolve()
# fmt:on


def persist_config(
    path: Optional[Union[Path, str]], force: bool = False
) -> Tuple[bool, str, str]:
    p: Path = Path(DEFAULT_CONFIG_FILE if path is None else path)
    content: str = ""
    exists: bool = p.exists()

    if exists and not force:
        content = pytomlpp.dumps(load_config(p))
    else:
        content = pytomlpp.dumps(DEFAULT_CONFIG)
        if not p.parent.exists():
            p.parent.mkdir(parents=True, exist_ok=True)

        with open(p, mode="w") as new_cfg:
            new_cfg.write(content)

    return exists, str(p), content


def load_config(path) -> dict:
    with open(Path(path).expanduser().resolve(), mode="r") as cfg:
        return pytomlpp.load(cfg)


def load_credentials(path, env: str) -> Tuple[str, str]:
    creds = load_config(path)
    return (creds["env"][env]["user"], creds["env"][env]["password"])
