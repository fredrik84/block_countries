#!/usr/bin/python3
from ipsetpy import ipset_version, ipset_create_set, ipset_add_entry, ipset_list, ipset_test_entry, ipset_flush_set, ipset_destroy_set
from argparse import ArgumentParser
import requests, re, logging
from html.parser import HTMLParser

parser = ArgumentParser()
parser.add_argument("--country", "-c", default="ch", action="store", help="Countries")
parser.add_argument("--list", "-l", action="store_true", help="List countries")
parser.add_argument("--add", "-a", action="store_true", help="Add countries")
parser.add_argument("--remove", "-r", action="store_true", help="Remove countries")
parser.add_argument("--clear", action="store_true", help="Clear ipset")
parser.add_argument("--logfile", default='/var/log/country_rbl.log', action="store", help="Logfile")
args = parser.parse_args()

logging.basicConfig(level=logging.INFO,
        format='[%(asctime)s] [%(levelname)-8s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=args.logfile,
        filemode="a"
    )
logger = logging.getLogger()

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def clear_sets():
  for set_name in ipset_list(name=True).split():
    ipset_destroy_set(set_name=set_name)

def create_set(set_name):
  ipset_create_set(set_name, type_name='hash:net')

if args.list:
  r = requests.get("http://www.ipdeny.com/ipblocks/data/countries/")
  country = list()
  for i in strip_tags(str(r.content)).split("\\n"):
    if re.match("^.*\.zone", i):
      country.append(i[:2])
  print("Available countries:")
  print("  %s" % ", ".join(country))
  exit()

if args.add:
  counter = 0
  new = False
  for country in args.country.split(","):
    logging.info("[%s] Fetching RBL" % country.upper())
    r = requests.get('http://www.ipdeny.com/ipblocks/data/countries/%s.zone' % country)
    block_list = r.content.split()
    sets = ipset_list(name=True).strip().split()
    if not country in sets:
      logging.info("[%s] IPSET set does not exist, creating" % country.upper())
      create_set(country)
      new = True
    logging.debug("[%s] Adding RBL to IPSET set" % country.upper())
    for ip in block_list:
      logging.debug("[%s] Adding entry %s" % (country.upper(), ip))
      if not new:
        if ipset_test_entry(country, ip):
          continue
      counter+=1
      ipset_add_entry(set_name=country, entry=ip)
    logging.info("[%s] Added %s new entries" % (country.upper(), counter))

if args.remove:
  logging.info("[%s] Clearing IPSET set" % (args.country.upper()))
  for country in args.country.split(","):
    ipset_destroy_set(set_name=country)

if args.clear:
  logging.info("[*] Clearing all IPSET sets")
  clear_sets()
