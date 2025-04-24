#!/bin/bash

ip addr flush dev eth0
ip addr add 10.0.16.20/24 dev eth0
ip link set eth0 up

ip addr flush dev eth1
ip addr add 10.0.18.10/24 dev eth1
ip link set eth1 up

/etc/init.d/frr start
exec bash