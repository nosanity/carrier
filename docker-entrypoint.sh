#!/bin/sh
# by Nick Lubyanov <lubyanov@gmail.com>

# DynIP
IP=$(cat /etc/hosts|grep $HOSTNAME |awk '{print $1}')
echo "IP $IP"
export CONFIG=openshift
echo starting
echo "current config = $CONFIG"

exec "$@"