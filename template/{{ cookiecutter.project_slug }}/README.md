{{ cookiecutter.project_name }}
===============================

`pyscriptenv` based application

> Assumes `pyscriptenv` and `pyscriptbuild` environments available under default path: `$HOME/bin`


Run from Source
---------------

```shell
# make sure pyscript primary env is active (default path shown)
. $HOME/bin/pyscriptenv/bin/activate

python -m {{ cookiecutter.project_module }} --help
python -m {{ cookiecutter.project_module }} --version
python -m {{ cookiecutter.project_module }} --show --default
```

Build and Install from Source
-----------------------------

```shell
# clean existing `dist` directory
rm -rf ./dist

# build wheel and sdist (default path for pyscript build env shown)
$HOME/bin/pyscriptbuild/bin/python -m build --skip-dependencies --no-isolation --wheel --sdist .

# install built wheel (default path for pyscript primary env shown)
$HOME/bin/pyscriptenv/bin/python -m pip install --no-deps --force-reinstall ./dist/*.whl
```

Running after Install
---------------------

```shell
# make sure pyscript primary env is active (default path shown)
. $HOME/bin/pyscriptenv/bin/activate

# app is installed as a runnable script via {{ cookiecutter.project_slug }} or {{ cookiecutter.project_module }}
{{ cookiecutter.project_slug }}
{{ cookiecutter.project_module }}

# all of these will work with the default configuration
{{ cookiecutter.project_slug }} --help
{{ cookiecutter.project_module }} --version
{{ cookiecutter.project_slug }} --show --default
```

Importing as a Module
---------------------

```python
# available in any pyscriptenv app from the module name
import {{ cookiecutter.project_module }} as {{ cookiecutter.project_slug }}
```
