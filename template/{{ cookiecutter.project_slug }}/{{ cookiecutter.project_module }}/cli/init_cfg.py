from pathlib import Path

import click

from .. import config
from ..config import DEFAULT_CONFIG, DEFAULT_CONFIG_FILE, DEFAULT_CONFIG_PATH
from . import utils


@click.command(
    help=f"""Persist a configuration file using internal config values.

    File path is set according to "--env" and "--dir" options
    (found on root command).

    Default file path:
    {DEFAULT_CONFIG_PATH / DEFAULT_CONFIG_FILE}""",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force overwrite of existing config file.",
)
@click.option(
    "--file",
    "filename",
    type=str,
    required=False,
    metavar="CONFIG_FILENAME",
    help="Configuration filename (overrides env based name).",
)
@click.pass_context
def init(ctx: click.Context, force, filename):
    # set default filename if not provided
    if filename is None:
        filename = f"{ctx.obj['root']['env']}.config.toml"

    # use config_dir field from root context for directory
    directory = Path(ctx.obj["root"]["config_dir"]).expanduser().resolve()
    path = directory / Path(filename)

    # init params
    ctx.obj["init"] = dict(
        force=force,
        config_file=filename,
        config_directory=directory,
        config_path=path,
    )

    # run show, exit on dry_run
    utils.show(ctx)

    # init config directory
    op = "created" if config.init_config_dir(directory) else "exists"
    click.secho(f"config directory {op} at {directory}", err=True, fg="yellow")

    # persist config file
    path_exists = path.exists()
    content = config.init_config_file(path, DEFAULT_CONFIG, force)

    op = "created" if not path_exists else ("overwritten" if force else "exists")
    click.secho(f"config file {op} at {path} with content:\n", err=True, fg="yellow")

    # output content of config file
    click.echo(content)
