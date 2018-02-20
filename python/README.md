# Dependencies:
APT: apt-get install ipset

PIP: pip3 install -r requirements.txt

# Add Ukraine, China and Russia, log output to path
sudo ./block.py --add --country ua,cn,ru --logfile </custom/path/to/logfile>

# Remove Ukraine from blocklist
sudo ./block.py --remove --country ua

# Get list of available zones from http://www.ipdeny.com/ipblocks/data/countries/
sudo ./block.py -l

# Delete all IPSET sets
sudo ./block.py --clear
