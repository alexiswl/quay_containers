#!/bin/bash

# Write echo to stderr
echoerr() { echo "$@" 1>&2; }

# Global variables (Debugger determined by DRY_RUN_CENTRIFUGE env variable)
## Name of software (for container, this may be different to the command)
SOFTWARE="lumpy"
## Software version
VERSION="0.2.14"
## WHAT Bind paths are to be set by default
BIND_PATHS_ARRAY=(/data /Databases)
## Would we like a clean environment 0: No, 1: Yes
CLEAN_ENV=1
## Do we need a specific app to run
APP="l_merge.py"

# Local variables (Standard between images)
HERE=$(dirname "${BASH_SOURCE[0]}")
CONTAINER_DIR=$(dirname ${HERE})
IMAGE=${CONTAINER_DIR}/image/${SOFTWARE}_${VERSION}.simg
SOFTWARE_UPPER=LUMPY
# Initialise command opts
COMMAND_OPTS=""

# Check for clean env
if [[ "${CLEAN_ENV}" == "1" ]]; then
        COMMAND_OPTS="${COMMAND_OPTS} --cleanenv"
elif [[ "${CLEAN_ENV}" == "0" ]]; then
        :
else
        echoerr "Clean env toggle not specified correctly, must be between zero or one, not ${CLEAN_ENV}"
        exit 1
fi

# Check debugger
if [[ -v DRY_RUN_${SOFTWARE_UPPER} ]]; then
        echoerr "This will be a dry-run of the software"
        DRY_RUN=$(eval 'echo "${DRY_RUN_'"${SOFTWARE_UPPER}"'}"')
        echoerr "Verbosity level has been set at ${DRY_RUN}"
else
        DRY_RUN=0
fi

# Check image exists
if [[ -f ${IMAGE} ]]; then
       :
else
        echoerr "Cannot find image. ${IMAGE} does not exist"
        exit 1
fi

# Check / add APP
if [[ ! -z ${APP} ]]; then
        # Evaulate grep
        grep -q ${APP} <(singularity apps ${IMAGE})
        # Check app is inside by using grep exit code
        if [[ "$?" == 0 ]]; then
                COMMAND_OPTS="${COMMAND_OPTS} --app ${APP}"
        else
                echoerr "Could not find app ${APP} in image ${IMAGE}"
                exit 1
        fi
fi

# Add in bind_paths
BIND_PATHS_STR=""
for BIND_PATH in "${BIND_PATHS_ARRAY[@]}"; do
        # Check path exists in filesystem before binding
        if [[ ! -d "${BIND_PATH}" ]]; then
                echoerr "Could not bind path ${BIND_PATH}. Exiting"
                exit 1
        else
                BIND_PATHS_STR="${BIND_PATHS_STR} --bind ${BIND_PATH}:${BIND_PATH}"
        fi
done

# Do we need to unset the xdg runtime dir
if [[ -v XDG_RUNTIME_DIR && ! -z "$XDG_RUNTIME_DIR" ]]; then
        unset XDG_RUNTIME_DIR
fi

# Merge as command options
if [[ ! -z ${BIND_PATHS_STR} ]]; then
        COMMAND_OPTS="${COMMAND_OPTS} ${BIND_PATHS_STR}"
fi

# Set command
COMMAND="singularity run ${COMMAND_OPTS} ${IMAGE}"

# Would you like to see the environment we're running it in
if [[ "${DRY_RUN}" == "2" ]]; then
        echoerr ""
        echoerr "### Printing out current environment ###"
        printenv 2>&1
        echoerr "### Completed printing of the environment ###"
        echoerr ""
fi

# Would you like to printout the command we're running
# Or run it instead?
if [[ ! "${DRY_RUN}" == "0" ]]; then
        echoerr ""
        echoerr "### Would have run command ###"
        echoerr "${COMMAND}" $(eval echo '"${@}"')
        echoerr "### Completed printing of the command ###"
        echoerr ""
else
        # Run command
        eval '${COMMAND}' '"${@}"'
fi

