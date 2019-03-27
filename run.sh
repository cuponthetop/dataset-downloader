#!/usr/bin/env bash

# Reset OPTIND
OPTIND=1

# suppress linter
CONTAINER_TAG=

# ARGUMENT
BUILD=FALSE
SCRIPT_ENV=
DETACHED=FALSE

# Check if any of variables in env are empty
# https://stackoverflow.com/questions/307503/whats-a-concise-way-to-check-that-environment-variables-are-set-in-a-unix-shell
export $(grep -v -e '^#' -e '^\s' env/docker.env | awk -F "=" '{print $1"=${"$1":?"$1"_required}"}')
export $(grep -v '^#' env/docker.env)

# Argument Parsing
while getopts "bds:" opt; do
    case "$opt" in
    b)  BUILD=TRUE
        ;;
    d)  DETACHED=TRUE
        ;;
    s)  SCRIPT_ENV=$OPTARG
        if [[ ! -f $(pwd)/env/${SCRIPT_ENV} ]]; then
            echo "Specified ${SCRIPT_ENV} is not found"
            exit 1
        elif [[ ${SCRIPT_ENV: -4} != ".env" ]]; then
            echo "Specified ${SCRIPT_ENV} is not .env file, specify .env file"
            exit 1
        fi
        ;;
    esac
done

if [[ ${BUILD} == "TRUE" ]]; then
    echo "Building Docker image for $(id)"

    docker build . -t ${CONTAINER_TAG} --build-arg uid=$(id -u) --build-arg gid=$(id -g)
fi

ADDITIONAL_ARG=""
if [[ ${DETACHED} == "TRUE" ]]; then
    ADDITIONAL_ARG="${ADDITIONAL_ARG} -d"
fi

# generate absolute path from environment
SCRIPT_LOCATION=$(readlink -f $(pwd)/${SCRIPT_LOCATION})
OUTPUT_LOCATION=$(readlink -f $(pwd)/${OUTPUT_LOCATION})
INPUT_LOCATION=$(readlink -f $(pwd)/${INPUT_LOCATION})
ENV_LOCATION=$(readlink -f $(pwd)/env)

# check if they exist, otherwise, terminate
if [[ ! -d ${SCRIPT_LOCATION} ]]; then
    echo "Script location ${SCRIPT_LOCATION} is not found, exiting"
    exit 1
fi
if [[ ! -d ${OUTPUT_LOCATION} ]]; then
    echo "Output location ${OUTPUT_LOCATION} is not found, creating"
    mkdir -p ${OUTPUT_LOCATION}
fi
if [[ ! -d ${INPUT_LOCATION} ]]; then
    echo "Input location ${INPUT_LOCATION} is not found, exiting"
    exit 1
fi
if [[ ! -d ${ENV_LOCATION} ]]; then
    echo "Environment location ${ENV_LOCATION} is not found, exiting"
    exit 1
fi

CONTAINER_NAME=${CONTAINER_TAG}

RUN_ARG=(-u $(id -u):$(id -g) \
    --name "${CONTAINER_NAME}" \
    --rm \
    -e "SCRIPT_ENV=${SCRIPT_ENV}" \
    -v "${SCRIPT_LOCATION}":/script \
    -v "${OUTPUT_LOCATION}":/output \
    -v "${ENV_LOCATION}":/env \
    -v "${INPUT_LOCATION}":/input \
    ${ADDITIONAL_ARG} \
    ${CONTAINER_TAG} "/shells/experiment.sh")

# stop and remove previous container
docker stop "${CONTAINER_NAME}"
docker rm "${CONTAINER_NAME}"

docker run "${RUN_ARG[@]}"