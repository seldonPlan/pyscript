#!/usr/bin/env sh

################################################################################
### simple packaging script for cookiecutter template
###
### Packages the template directory into `pyscript.template.zip`. Optionally
### copies zip file to $DEPLOY_PATH. Template is usable by the coookiecutter
### command as `cookiecutter $DEPLOY_PATH/pyscript.template.zip`
###
### Requirements
###  • `zip` command (tested with Info-ZIP utility stanaard on OSX)
################################################################################

set -o errexit -o noclobber -o nounset
# uncomment below for debug mode (i.e. `set -x`)
# set -o xtrace

# indicates if archive should be deployed to $DEPLOY_PATH, accepts: "deploy"|"yes"
DO_DEPLOY="${1:-NO}"
DEPLOY_PATH="${HOME}/bin"

# can be run from top level repo directory or one level deeper (ex. scripts dir)
TARGET_DIR=""
if [ -r ../cookiecutter.json ]; then
    TARGET_DIR="$(readlink -e "$(pwd)/../")"
else
    if [ -r ./cookiecutter.json ]; then
        TARGET_DIR="$(pwd)"
    else
        echo "ERROR cant find target directory with cookiecutter.json file"
        exit 1
    fi
fi

TARGET_NAME="$(basename "${TARGET_DIR}")"

# output directory
printf "=====[ %-30s ]=========================================\n" "Resetting build Directory"
rm -rf "${TARGET_DIR}/build"
mkdir "${TARGET_DIR}/build"

# ensure archive is built with proper root level dir
cd "${TARGET_DIR}/.."

# create archive
printf "=====[ %-30s ]=========================================\n" "Zipping Template"
zip --recurse-paths -9 \
    "${TARGET_DIR}/build/pyscript.template.zip" \
    "${TARGET_NAME}"/ \
    --exclude \
        "${TARGET_NAME}/.git/*" \
        "${TARGET_NAME}/build/*" \
        "${TARGET_NAME}/scripts/*" \
        "${TARGET_NAME}/.gitignore" \
        "${TARGET_NAME}/.DS_Store" \
        "${TARGET_NAME}/.mypy_cache/*"

printf "=====[ %-30s ]=========================================\n" "Zip File"
ls -lhA "${TARGET_DIR}/build/pyscript.template.zip"

case "${DO_DEPLOY}" in
    deploy|DEPLOY|yes|YES|y|Y)
        printf "=====[ %-30s ]=========================================\n" "Deploying Template"
        cp -i -t "${DEPLOY_PATH}" "${TARGET_DIR}/build/pyscript.template.zip"
        ls -lhA "${DEPLOY_PATH}/pyscript.template.zip"
        ;;
    *)
        exit 0
esac
