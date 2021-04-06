import json
from pathlib import Path

import click

from . import __version__
from .config import (
    DEFAULT_CONFIG,
    DEFAULT_CONFIG_FILE,
    init_config_file,
    load_config_file,
)


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
    type=click.Path(file_okay=True, dir_okay=False, readable=True, resolve_path=True),
    help="Config file path.",
)
@click.option(
    "--default",
    is_flag=True,
    help="""Do not load a config file, using default instead
            ("--config" is ignored)""",
)
@click.option(
    "--init",
    is_flag=True,
    help=f"""Initializes a new configuration file with the default config dict.

             \b
             Default location (when no "--config" provided):
             {DEFAULT_CONFIG_FILE}
             will not overwrite existing file
             only --config option is read, all others ignored""",
)
@click.version_option(__version__, "--version", "-v", message="v%(version)s")
@click.pass_context
def cli(
    ctx, color: bool, dry_run: bool, show: bool, config: Path, default: bool, init: bool
):
    # automatically handle all color opts with context attr
    ctx.color = color

    # escapes further processing if we are initializing a new config file
    _init_config_file(ctx, init, config)

    # make cli, app configs available on context object
    _set_context(ctx, color, dry_run, show, default, config)

    # example functionality, replace with app functionality
    _show(ctx)
    click.secho("{{ cookiecutter.project_module }}.cli works!", fg="yellow")


def _set_context(ctx, color, dry_run, show, default, config):
    """populates context attr with relevant config values to be used in subcommands"""
    ctx.ensure_object(dict)

    # cli config
    # store option values
    ctx.obj["cli"] = dict(
        color="auto" if color is None else color,
        dry_run=dry_run,
        show=show,
        config_file=DEFAULT_CONFIG_FILE if config is None else config,
        use_default_config=default,
    )

    # app config
    # use internal config if requested (overrides other options)
    if default:
        ctx.obj["config"] = DEFAULT_CONFIG
    # attempt to load config file if requested
    elif config is not None:
        try:
            ctx.obj["config"] = load_config_file(config)
        except FileNotFoundError:
            raise click.UsageError(
                f"Invalid value for '--config': File '{config}' does not exist.", ctx
            )
    # otherwise attempt to load default config file location
    # falling back to internal config if needed
    else:
        try:
            ctx.obj["config"] = load_config_file(DEFAULT_CONFIG_FILE)
        except FileNotFoundError:
            click.secho(
                (
                    "WARNING: default config file not found,"
                    " using internal configuration instead"
                ),
                err=True,
                fg="yellow",
            )
            ctx.obj["config"] = DEFAULT_CONFIG


def _init_config_file(ctx, init, config):
    """Short circuiting method that checks the "--init" flag,
    and, when set, attempts to create new config file with default values
     - Will not overwrite an existing file
     - Outputs the file contents of new file or existing file
     - Exits app when done, ignoring any other flags or commands
    """
    if init:
        exists, path, content = init_config_file(config)
        click.secho(
            (
                f"default config {'exists' if exists else 'created'} "
                f"at {path} with content:\n"
            ),
            err=True,
            fg="yellow",
        )
        click.echo(content)
        ctx.exit(0)


def _show(ctx):
    """convenience method to print full context object to STDERR if requested via
    the "--show" or "--dry-run" flags.

    "--dry-run" flag check also exits app when set
    """
    if ctx.obj["cli"]["show"] or ctx.obj["cli"]["dry_run"]:
        click.secho(
            f"{json.dumps(ctx.obj,default=lambda o: str(o),sort_keys=True,indent=4)}",
            err=True,
        )

    if ctx.obj["cli"]["dry_run"]:
        ctx.exit(0)
