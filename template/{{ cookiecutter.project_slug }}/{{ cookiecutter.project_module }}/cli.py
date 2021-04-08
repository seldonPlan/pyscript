from pathlib import Path

import click

from . import __version__
from . import cli_utils as utils
from .config import DEFAULT_CONFIG_FILE


@click.group(
    name="{{ cookiecutter.project_slug }}",
    invoke_without_command=True,
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.option(
    "--color/--no-color", " /-n", "color", default=None, help="Enable/Disable colors."
)
@click.option(
    "--dry-run", "-d", is_flag=True, help="Show configuration, dont run command."
)
@click.option("--show", "-s", is_flag=True, help="Show configuration.")
@click.option(
    "--config",
    "config_file",
    type=click.Path(file_okay=True, dir_okay=False, readable=True, resolve_path=True),
    default=None,
    help="Config file path.",
)
@click.option(
    "--default",
    is_flag=True,
    help="""Do not load a config file, force internal default config
            ("--config" is ignored)""",
)
@click.option(
    "--env",
    type=str,
    default="default",
    help="Configured environment name",
    metavar="ENV_NAME",
)
@click.version_option(__version__, "--version", "-v", message="v%(version)s")
@click.pass_context
def cli(
    ctx: click.Context,
    color: bool,
    dry_run: bool,
    show: bool,
    config_file: Path,
    default: bool,
    env: bool,
):
    # automatically handle all color opts with context attr
    ctx.color = color

    # make cli, app configs available on context object
    utils.set_context(ctx, color, dry_run, show, default, config_file, env)

    # example functionality, replace with app functionality
    click.secho("{{ cookiecutter.project_module }}.cli works!", fg="yellow")


@cli.command(
    help=f"""Persist a new configuration file.

    \b
    Default location (if CONFIG_FILE not provided):
    {DEFAULT_CONFIG_FILE}

    \b
    Use "--force" to overwrite existing configuration file"""
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force overwrite existing config file.",
)
@click.argument(
    "config_file",
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        resolve_path=True,
    ),
    default=DEFAULT_CONFIG_FILE,
    required=False,
    metavar="CONFIG_FILE",
)
@utils.show_config(do_exit=True)
@click.pass_context
def init(ctx, force, config_file):
    utils.init(ctx, force, config_file)
