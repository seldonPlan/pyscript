Pyscript Application Template
=============================

[cookiecutter](https://cookiecutter.readthedocs.io/en/1.7.2/index.html) template definition to generate a python application that is runnable under a Pyscript primary env and buildable with the Pyscript build environment.


Generating an Application from this Template
--------------------------------------------

> if installed via pipx, available as `cookiecutter`

> if installed via pip, available as `python -m cookiecutter`

```bash


# provide template params on the cli
cookiecutter --no-input --output-dir /path/to/parent/dir /path/to/template/dir \
    project_name="Awesome App" \
    author="Your Name <your@email.com>" \
    homepage="https://github.com/example" \
    install_vscode_project="yes" \
    install_pre_commit_hooks="yes"

# alternatively, copy and edit `example_template_config.yaml` and pass to cli
cookiecutter --no-input  --config-file config.yaml --output-dir /path/to/parent/dir /path/to/template/dir
```


Generated Application Structure
-------------------------------

> review `cookiecutter.json` file for variable values

```
${project_slug}/
   ├── .vscode/
   │   ├── tasks.json
   │   ├── launch.json
   │   └── workspace.code-workspace
   ├── ${project_module}/
   │   ├── __init__.py
   │   ├── __main__.py
   │   ├── cli.py
   │   ├── config.py
   │   └── ...
   ├── .pre-commit-config.yaml
   ├── .flake8
   ├── .gitignore
   ├── pyproject.toml
   └── README.md
```


Building a Template Archive File
--------------------------------

Packages pyscript template as a zip file in `build/pyscript.template.zip`. Can be used in place of template directory argument in `cookiecutter` command

```bash
# make script executable
chmod u+x scripts/build_archive.sh

# generates `build/pyscript.template.zip`
scripts/build_archive.sh

# alternatively, generate `build/pyscript.template.zip` and prompt to copy to `$DEPLOY_DIR` directory
scripts/build_archive.sh y
```
