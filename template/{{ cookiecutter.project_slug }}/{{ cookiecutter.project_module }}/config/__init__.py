from pathlib import Path
from typing import Optional, Union, cast

import pytomlpp

from .default import DEFAULT_CONFIG

# fmt: off
__all__ = [
    "DEFAULT_CONFIG", "DEFAULT_CONFIG_PATH", "DEFAULT_CONFIG_FILE",
    "source_list", "merge_configs", "load_toml",
    "init_config_file", "init_config_dir",
]


DEFAULT_CONFIG_PATH = (
    Path("{{ cookiecutter.project_default_config_root }}/{{ cookiecutter.project_slug }}")  # noqa: E501
    .expanduser()
    .resolve()
)
DEFAULT_CONFIG_FILE = Path("{{ cookiecutter.project_default_config_file }}")  # noqa: E501
# fmt: on


def source_list(
    env: str, default: bool, config_dir: str, config_file: Optional[str]
) -> list[Union[Path, str]]:
    if default:
        return ["INTERNAL"]

    if config_file is not None:
        return [Path(config_file).expanduser().resolve()]

    path: Path = Path(config_dir)
    output: list[Union[Path, str]] = []

    def_cfg_file = (path / "default.config.toml").expanduser().resolve()
    env_cfg_file = (path / f"{env}.config.toml").expanduser().resolve()

    output.append(def_cfg_file if def_cfg_file.exists() else "INTERNAL")
    if env != "default" and env_cfg_file.exists():
        output.append(env_cfg_file)

    return output


def merge_configs(sources: list[Union[Path, str]]) -> dict:
    output: dict = {}

    for source in sources:
        if source == "INTERNAL":
            output = {**output, **DEFAULT_CONFIG}
            continue

        output = {**output, **load_toml(cast(Path, source))}

    return output


def init_config_dir(config_dir: Path = DEFAULT_CONFIG_PATH) -> bool:
    if config_dir.exists() and not config_dir.is_dir():
        raise FileExistsError(
            "Unable to create config directory, path exists and is not a directory",
            config_dir,
        )

    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
        return True

    return False


def init_config_file(path: Path, content: dict, force: bool = False) -> dict:
    if not path.exists() or (path.exists() and force):
        with open(file=path, mode="wt", encoding="utf8") as f:
            f.write(pytomlpp.dumps(content))
            f.write("\n")
            return content

    if path.exists():
        with open(file=path, mode="rt", encoding="utf8") as f:
            return pytomlpp.load(f)

    return content


def load_toml(path: Path) -> dict:
    with open(path, mode="rt", encoding="utf8") as cfg:
        return pytomlpp.load(cfg)
