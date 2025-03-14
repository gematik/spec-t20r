#!/bin/bash

# Build rs-vsdm2-app

# Name des Clusters
CLUSTER_NAME="zeta-guard"

# Docker-Image, das in den Cluster geladen werden soll
DOCKERFILE_PATH="resource-server/src/Dockerfile"
DOCKER_IMAGE="rs-vsdm2-app:latest"

# Build the Docker image
docker build -t "${DOCKER_IMAGE}" -f "${DOCKERFILE_PATH}" resource-server/src

# Load the Docker image into the kind cluster
kind load docker-image "${DOCKER_IMAGE}" --name "${CLUSTER_NAME}"
