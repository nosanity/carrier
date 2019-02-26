#!/bin/sh
# by Evgeniy Bondarenko <Bondarenko.Hub@gmail.com>
# v5   add tmp variable $first_run for run Build static and localization
# v4.3 edit for variable for default Openshift envaroment

# DynIP
IP=$(cat /etc/hosts|grep $HOSTNAME |awk '{print $1}')
#export IP=${IP:-"127.0.0.1"}
echo "IP $IP"
export CONFIG=openshift
echo "current config $CONFIG"

echo starting

exec "$@"