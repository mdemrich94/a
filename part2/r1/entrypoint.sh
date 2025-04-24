#!/bin/bash

ip addr flush dev eth0
ip addr add 10.0.14.20/24 dev eth0
ip link set eth0 up

ip addr flush dev eth1
ip addr add 10.0.16.10/24 dev eth1
ip link set eth1 up

ip addr flush dev eth2
ip addr add 10.0.17.10/24 dev eth2
ip link set eth2 up

/etc/init.d/frr start
exec bash