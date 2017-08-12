#!/bin/bash

ROOTDIR=$PWD
UNBOUND_INSTALL=$ROOTDIR/target

mkdir -p ${UNBOUND_INSTALL}

pushd unbound-1.6.4

if ! ./configure --prefix=${UNBOUND_INSTALL} --with-pythonmodule
then
  echo "Configuration failed"
  exit 1
fi

if ! make
then
  echo "Make failed"
  exit 2
fi

if ! make install
then
  echo "Installation failed"
  exit 3
fi
popd
