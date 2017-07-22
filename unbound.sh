#!/bin/bash

ROOTDIR=$PWD
UNBOUND_INSTALL=$ROOTDIR/unbound

mkdir -p ${UNBOUND_INSTALL}

pushd unbound-1.6.4

./configure --prefix=${UNBOUND_INSTALL} --with-pythonmodule && make && make install

popd
