pyscript environment
====================

The `pyscript` environment is a recipe for an opinionated, python3 virtual environment, emphasizing rapid building of small, robust, easy-to-use applications for everyday use. 

Pyscript applications are intended to fill a niche that exists between small "hacked together" scripts and large, widely distributed projects. Despite being small and built quickly, a Pyscript application follows rigorous code quality practices by default. Additionally, Pyscript applications are flexible, being able to be easily run as a standalone cli or as an imported module in another python application.

**Features**

 - easily deployed templates to get up and running quickly
 - built-in code quality tooling with `black`, `flake8`, `isort`, and `mypy`
 - integration with VS Code `python` extension
 - utilizes `git` to track changes
 - validate commit quality with rigorous `pre-commit` hooks
 - lean dependencies


Bootstrap a Pyscript Environment
--------------------------------

**Requirements**

 - modern Python 3 installation (`python>=3.6`)
 - `pipx` (for development dependencies)

```bash
# make the setup scripts executable
chmod u+x ./pyscript-tools.py
chmod u+x ./pyscript-init.py

# validate they can be run by reviewing their help output
./pyscript-tools.py --help
./pyscript-init.py --help

# setup development environment tooling
# (wraps pipx actions to install predefined list of tools)
./pyscript-tools.py install

# setup pyscript primary and build envs with defaults
# (depends on virtualenv, one of the tool )
./pyscript-init.py
```


Getting Started with a Pyscript Template
----------------------------------------

New pyscript applications can be quickly setup using the template script.

```bash
# make the setup scripts executable
chmod u+x ./pyscript-template.py

# generate pyscript application with NAME, under /path/to/parent
./pyscript-template.py --path /path/to/parent NAME
```

See README under `template/` directory for details on what is generated, and creating a template config file.


Pyscript Build and Primary Environments
---------------------------------------

The pyscript environment consists of two installed virtualenvs named, **`primary`** and **`build`**

### `build` Environment ###

> default install location: `${HOME}/bin/pyscriptbuild`

Contains only what is needed to perform a build for a custom application. This environment includes PEP-517/518 compliant tooling:
   - PyPA `build` tool
   - `flit-core`

### `primary` Environment ###

> default install location: `${HOME}/bin/pyscriptenv`

Contains all runtime dependencies and installed executables for custom applications. Completed pyscript applications can be added by `pip install`, along with standard dependencies as well.


Anatomy of a Pyscript Application
---------------------------------

A pyscript application by default has a number of (opinionated) design choices with the goal of getting up and running quickly.

```
${app_name}/
   ├── .vscode/
   │   ├── tasks.json
   │   ├── launch.json
   │   └── workspace.code-workspace
   ├── pyscript_${app_name}/
   │   ├── __init__.py
   │   ├── __main__.py
   │   ├── cli/
   │   │   ├── __init__.py
   │   │   ├── root.py
   │   │   ├── utils.py
   │   │   └── ...
   │   ├── config/
   │   │   ├── __init__.py
   │   │   ├── default.py
   │   │   └── ...
   │   ├── logging/
   │   │   ├── __init__.py
   │   │   └── ...
   │   └── ...
   ├── .pre-commit-config.yaml
   ├── .flake8
   ├── .gitignore
   ├── pyproject.toml
   └── README.md
```

### `pyproject.toml` ###

All pyscript applications use `pyproject.toml` as the primary entrypoint for build/installation. There are many benefits to this approach, but suffice it to say, that it keeps things simple and predictable when building python applications.

The module name defaults to `pyscript_${app_name}`. This is done to make custom Pyscript applications easily recognizable in a pip list, or in code. The executable entry point defaults to `${app_name}` and `pyscript_${app_name}`

```toml
[build-system]
requires = ["flit_core >=3,<4"]
build-backend = "flit_core.buildapi"

[tool.flit.metadata]
module = "pyscript_${app_name}"
author = "${author_name}"
home-page = "${home_page}"
requires = [
    # default dependencies
    "click==7.1.2",
    "colorama==0.4.4",
    "pytomlpp==0.3.5",
]
requires-python=">=3.6"

[tool.flit.scripts]
# makes app executable by name upon install
${app_name} = "pyscriptenv_${app_name}:cli"
pyscriptenv_${app_name} = "pyscriptenv_${app_name}:cli"
```

Pyscript applications also takes advantage of tooling configuration in `pyproject.toml` where possible (c'mon `flake8`!)

```toml
[tool.black]
line-length = 88
target-version = ['py38']
include = 'pyscriptenv_${app_name}/.*\.py$'

[tool.isort]
profile = "black"
src_paths = ["pyscriptenv_${app_name}"]
filter_files = true
skip_gitignore = false

[tool.mypy]
ignore_missing_imports = true
follow_imports = "silent"
show_column_numbers = true
show_error_context = true
show_error_code = true
pretty = true

[tool.flake8]
# no support yet for flake8 in pyproject.toml, see .flake8 file
```

### `.pre-commit-config.yaml` ###

`pre-commit` configuration can be optionally added to any Pyscript application template. This can be installed as a hook to each commit, or just used as a useful bundle of code quality tools.

The `pre-commit` config is purposely strict to force a habit of code quality. This can, of course, be adjusted per individual preferences.

### `.vscode/` ###

A VS Code workspace can be optionally included in each Pyscript application. This workspace integrates nicely with the installed Pyscript environments, and development tools installed in the "Getting Started" section.

 - points `python.pythonPath` to the Pyscript **`primary`** environment python
 - code quality tooling (`black`, `flake8`, `isort`, `mypy`) point to the pipx installed versions of these tools
 - task set to run `pre-commit` checks on the project or individual files
 - task set to bump the application version (major, minor, or patch)
   - *note: this requires a functioning `grep` installation*
 - task to build using the Pyscript **`build`** environment, and install into the Pyscript **`primary`** environment
 - launch configuration to debug application from within VS Code

### `click` ###

A functional command line interface is provided by default in each new Pyscript application template. The `click` library (**C**ommand **L**ine **I**nterface **C**reation **K**it) is used for this.

By default, the following is enabled for every app:

 - color output support with `--color/--no-color`
 - `--dry-run` flag
 - toml configuration file initialization
 - `--default` flag to bypass configuration file altogether
 - `click.Context` population of all relevant cli, and application config
 - use `--show` flag to print configuration (useful for debugging, and verbose outputs)

All cli operations are segregated to the `cli.py` file, allowing applications to easily add importable modules, while also keeping useful functionality available on the cli.

### `flit-core` ###

`flit-core` defines some simplified defaults for defining project metadata

 - application version is defined in the root `__init__.py` using the `__version__` attribute
 - application description is also grabbed from the `__init__.py` docstring
