#!/usr/bin/env sh

apt-get update
apt-get install -y make

cd /vagrant
export NONINTERACTIVE=1
make sysdeps && make install
