from pathlib import Path
from typing import Optional, Tuple, Union

import pytomlpp

from .default import DEFAULT_CONFIG

# fmt:off
DEFAULT_CONFIG_FILE = (
    Path("{{ cookiecutter.project_default_config_root }}") / "{{ cookiecutter.project_slug }}" / "{{ cookiecutter.project_default_config_file }}"  # noqa: E501
).expanduser().resolve()
# fmt:on


def init_config_file(path: Optional[Union[Path, str]]) -> Tuple[bool, str, str]:
    _path: Path = Path(DEFAULT_CONFIG_FILE if path is None else path)
    _content: str = ""
    _exists: bool = _path.exists()

    if _exists:
        with open(_path, mode="r") as existing_cfg:
            _content = existing_cfg.read()
    else:
        _content = pytomlpp.dumps(DEFAULT_CONFIG)
        if not _path.parent.exists():
            _path.parent.mkdir(parents=True, exist_ok=True)

        with open(_path, mode="w") as new_cfg:
            new_cfg.write(_content)

    return _exists, str(_path), _content


def load_config_file(path: Optional[Path]) -> dict:
    output = {**DEFAULT_CONFIG}

    if path is None:
        return output

    try:
        with open(path, mode="r") as cfg:
            output = pytomlpp.load(cfg)
    except FileNotFoundError:
        if str(path) != str(DEFAULT_CONFIG_FILE):
            raise

    return output
