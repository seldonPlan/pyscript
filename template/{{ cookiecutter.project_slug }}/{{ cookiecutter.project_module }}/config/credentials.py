from pathlib import Path
from typing import Tuple

from . import load_toml


def load_credentials(path: Path, env: str) -> Tuple[str, str]:
    creds = load_toml(path)
    return (creds["user"], creds["password"])
