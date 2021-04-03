import shutil
import subprocess

print("post_gen_project script...")

if "{{ cookiecutter.install_vscode_project }}" == "no":
    print("removing vscode project files as requested...")
    shutil.rmtree(".vscode", ignore_errors=True)

if shutil.which("git") is not None:
    print("initializing git repo...")
    subprocess.run(["git", "init", "--quiet", "--initial-branch=develop"])
    subprocess.run(["git", "add", "."])

    # git is required to run pre-commit checks
    if shutil.which("pre-commit") is not None:
        if "{{ cookiecutter.install_pre_commit_hooks }}" == "yes":
            print("installing pre-commit hooks...")
            subprocess.run(["pre-commit", "install"])
    else:
        print("no pre-commit command found, skipping pre-commit checks...")

    subprocess.run(["git", "commit", "-m", "initial commit"])
else:
    print("no git command found, skipping git and pre-commit init...")
