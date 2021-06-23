import json

import click

from .. import __version__, config

spec = {
    "root": {
        "color": click.option(
            "--color/--no-color",
            " /-n",
            "color",
            default=None,
            help="Enable/Disable colors.",
        ),
        "dry-run": click.option(
            "--dry-run",
            "-d",
            is_flag=True,
            help="Show configuration, dont run command.",
        ),
        "show": click.option(
            "--show",
            "-s",
            is_flag=True,
            help="Show configuration.",
        ),
        "config": click.option(
            "--config",
            "config_file",
            type=click.Path(
                file_okay=True, dir_okay=False, readable=True, resolve_path=True
            ),
            default=None,
            help="Load only this config file, ignore any others.",
        ),
        "dir": click.option(
            "--dir",
            "config_dir",
            type=click.Path(
                file_okay=False, dir_okay=True, readable=True, resolve_path=True
            ),
            default=config.DEFAULT_CONFIG_PATH,
            help="Override default config directory",
        ),
        "default": click.option(
            "--default",
            is_flag=True,
            help="""Do not load any config file, use internal default config instead
                    ("--config" is ignored)""",
        ),
        "env": click.option(
            "--env",
            type=str,
            default="default",
            help="Configured environment name, informs what config files to merge.",
            metavar="ENV_NAME",
        ),
        "version": click.version_option(
            __version__,
            "--version",
            "-v",
            message="v%(version)s",
        ),
    },
}


def root_params(fn):
    """example of combining common params together under a single decorator

    use as `@root_params` to add all listed params to the command
    """
    fn = spec["root"]["color"](fn)
    fn = spec["root"]["dry-run"](fn)
    fn = spec["root"]["show"](fn)
    fn = spec["root"]["config"](fn)
    fn = spec["root"]["dir"](fn)
    fn = spec["root"]["default"](fn)
    fn = spec["root"]["env"](fn)
    fn = spec["root"]["version"](fn)
    return fn


def show(ctx, do_exit: bool = True):
    if ctx.obj["root"]["show"] or ctx.obj["root"]["dry_run"]:
        output = json.dumps(
            ctx.obj,
            default=lambda o: str(o),
            sort_keys=True,
            indent=4,
        )
        click.secho(f"{output}", err=True)

    if ctx.obj["root"]["dry_run"] and do_exit:
        ctx.exit(0)
