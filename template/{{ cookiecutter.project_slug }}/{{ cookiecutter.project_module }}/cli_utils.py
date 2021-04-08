import json
from functools import update_wrapper
from pathlib import Path

import click

from . import config


def set_context(ctx, color, dry_run, show, default, config_file, env):
    ctx.ensure_object(dict)

    # cli config
    # store option values
    ctx.obj["cli"] = dict(
        color="auto" if color is None else color,
        dry_run=dry_run,
        show=show,
        config_file=config_file,
        force_default=default,
        env=env,
    )
    normalize_config_file(ctx)


def init(ctx, force, config_file):
    exists, path, content = config.persist_config(config_file, force)
    op = "created" if not exists else ("overwritten" if force else "exists")

    click.secho(
        f"config {op} at {path} with content:\n",
        err=True,
        fg="yellow",
    )
    click.echo(content)
    ctx.exit(0)


def show_config(do_exit: bool = True):
    def decorator(f):
        def new_func(*args, **kwargs):
            ctx = click.get_current_context()
            show(ctx, do_exit)
            return ctx.invoke(f, *args, **kwargs)

        return update_wrapper(new_func, f)

    return decorator


def show(ctx, do_exit: bool = True):
    if ctx.obj["cli"]["show"] or ctx.obj["cli"]["dry_run"]:
        output = json.dumps(
            ctx.obj,
            default=lambda o: str(o),
            sort_keys=True,
            indent=4,
        )
        click.secho(f"{output}", err=True)

    if ctx.obj["cli"]["dry_run"] and do_exit:
        ctx.exit(0)


def normalize_config_file(ctx):
    # use internal config if requested (ignores other options)
    if ctx.obj["cli"]["force_default"]:
        ctx.obj["config"] = config.DEFAULT_CONFIG
        ctx.obj["cli"]["config_file"] = None

    # attempt to load config file if requested
    elif ctx.obj["cli"]["config_file"] is not None:
        try:
            ctx.obj["config"] = config.load_config(ctx.obj["cli"]["config_file"])
        except FileNotFoundError:
            raise click.UsageError(
                f"File '{ctx.obj['cli']['config_file']}' not found"
            ) from None

    # otherwise attempt to load default config file location
    # falling back to internal config if needed
    else:
        try:
            ctx.obj["config"] = config.load_config(config.DEFAULT_CONFIG_FILE)
            ctx.obj["cli"]["config_file"] = config.DEFAULT_CONFIG_FILE
        except FileNotFoundError:
            ctx.obj["config"] = config.DEFAULT_CONFIG
            ctx.obj["cli"]["config_file"] = None


def normalize_env_path(ctx, option, key, default_value=None):
    env = ctx.obj["cli"]["env"]

    # use option if defined
    if option is not None:
        ctx.obj["config"]["env"][env][key] = option

    # set to default if present, otherwise raise option error
    elif (
        key not in ctx.obj["config"]["env"][env]
        or ctx.obj["config"]["env"][env][key] is None
        or len(ctx.obj["config"]["env"][env][key]) == 0
    ):
        if default_value is None:
            raise click.BadOptionUsage(
                key, f"no {key} supplied, or present in configuration"
            )

        ctx.obj["config"]["env"][env][key] = default_value

    # otherwise keep configured value
    # normalize value
    ctx.obj["config"]["env"][env][key] = (
        Path(ctx.obj["config"]["env"][env][key]).expanduser().resolve()
    )
    ctx.obj["cli"][key] = ctx.obj["config"]["env"][env][key]


def parse_credentials(ctx):
    try:
        return config.load_credentials(
            ctx.obj["cli"]["credentials_file"], ctx.obj["cli"]["env"]
        )
    except:  # noqa: E722
        raise click.ClickException(
            "unable to parse credentials file "
            f"{str(ctx.obj['cli']['credentials_file'])}"
        )
