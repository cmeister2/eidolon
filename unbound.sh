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

# Copy the generated python module to the target as 'make install' does not do this.
if ! cp -v pythonmod/unboundmodule.py ${UNBOUND_INSTALL}
then
  echo "Failed to copy python module to ${UNBOUND_INSTALL}"
  exit 4
fi

popd
