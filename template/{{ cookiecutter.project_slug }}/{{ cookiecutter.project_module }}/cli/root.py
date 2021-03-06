from pathlib import Path
from typing import Optional

import click

from .. import config, logging
from . import utils


@click.group(
    name="{{ cookiecutter.project_slug }}",
    invoke_without_command=True,
    context_settings=dict(help_option_names=["-h", "--help"]),
    help="",
)
@utils.root_params
@click.pass_context
def root(
    ctx: click.Context,
    color: Optional[bool],
    dry_run: bool,
    show: bool,
    verbose: int,
    quiet: bool,
    config_file: Optional[str],
    config_dir: str,
    default: bool,
    env: str,
):
    """root command, sets up base application state used by sub-commands

    responsible for:
     * output styling and verbosity
       - `color` output management for all click.secho/click.style functions
       - `dry_run` flag for sub-commands to implement (use with utils.show function)
       - `show` flag for sub-commands to print config (use with utils.show function)
       - `verbose` flag, use with logging library module to manage output verbosity
       - `quiet` flag, use with logging library module to manage output verbosity

     * configuration management
       - `config_file` force configuration load from specified file only
       - `default` forces configuration load from internal values only
       - `config_dir` use configuration files from specified directory

     * environment management
       - `env` value identifies which config files to load and merge for app config
          (superseded by `config_file` and `default` options)
       - maintains list of configuration sources used

     * context initialization
       - instantiates a click.Context object to store configuration, and cli params
    """

    # automatically handle all color options with context attribute
    ctx.color = color

    # make cli, app configs available on context object
    ctx.ensure_object(dict)

    # root params
    ctx.obj["root"] = dict(
        color="auto" if color is None else color,
        dry_run=dry_run,
        show=show,
        log_level=logging.verbosity(verbose, quiet),
        config_dir=Path(config_dir).expanduser().resolve(),
        force_config_file=config_file,
        force_default=default,
        env=env.lower(),
        cmd=ctx.invoked_subcommand,
    )

    # set config
    ctx.obj["config_sources"] = config.source_list(
        env.lower(), default, config_dir, config_file
    )
    ctx.obj["config"] = config.merge_configs(ctx.obj["config_sources"])

    # configure logging, setup level, file logging, output options
    # options documented in logging module
    logging.configRootLogger(ctx.obj["root"]["log_level"]["value"])

    # default behavior without subcommand
    if ctx.invoked_subcommand is None:
        click.secho(
            "{{ cookiecutter.project_module }} cli works!",
            err=True,
            fg="yellow",
        )
        utils.show(ctx)
