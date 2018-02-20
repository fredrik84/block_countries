#!/bin/bash
declare -a countries
countries=(ch rn ua)

# remove blocking for a country
function remove() {
  rm -f /etc/country_blocks/$1.zone
  [ "$(ipset list -n | grep $1)" == "$1" ] && ipset destroy $1
}

# Add blocking for a country
function block_country() {
  [ -d /etc/country_blocks/ ] || mkdir -p /etc/country_blocks
  wget -q -P /etc/country_blocks/ http://www.ipdeny.com/ipblocks/data/countries/$1.zone || return 1

  [ "$(ipset list -n | grep $1)" == "$1" ] || ipset -N $1 hash:net

  for i in $(cat /etc/country_blocks/$1.zone); do
    ipset -A $1 $i
  done
}

# Start/stop/reload functions
function start_block() {
  [ -f /etc/iptables.firewall.rules ] && iptables-restore < /etc/iptables.firewall.rules

  for cn in ${countries[*]}; do
    remove $cn
    block_country $cn
  done
}

function stop_block() {
  for cn in ${countries[*]}; do
    remove $cn
  done

  [ -f /etc/iptables.firewall.rules ] && iptables-restore < /etc/iptables.firewall.rules
}

function reload_block() {
  for cn in countries; do
    block_country $cn
  done
}

case $1 in
  start)
      start_block
    ;;
  stop)
      stop_block
    ;;
  reload)
      reload_block
    ;;
  restart)
      stop_block
      start_block
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|reload}"
    ;;
esac
