#!/bin/bash

ip addr flush dev eth0
ip addr add 10.0.14.10/24 dev eth0
ip link set eth0 up

exec bash