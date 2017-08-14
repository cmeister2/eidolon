#!/usr/bin/env bash

set -ex

echo "Pull request: ${TRAVIS_PULL_REQUEST}"
echo "Branch: ${TRAVIS_BRANCH}"

if [[ ${TRAVIS_PULL_REQUEST} == "false" ]]
then
  if [[ ${TRAVIS_BRANCH} == "master" ]]
  then
    docker push cmeister2/eidolon:$DATA_SOURCE
  fi
fi