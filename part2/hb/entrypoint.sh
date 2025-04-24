#!/bin/bash

ip addr flush dev eth0
ip addr add 10.0.15.20/24 dev eth0
ip link set eth0 up

exec bash