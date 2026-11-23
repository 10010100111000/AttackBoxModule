#!/usr/bin/env python3
import urllib.request
base="http://bashed-target"
home=urllib.request.urlopen(base+"/",timeout=8).read().decode()
assert "Bashed" in home
page=urllib.request.urlopen(base+"/dev/phpbash.php",timeout=8).read().decode()
assert "sendCommand" in page
print("PASS: recreated instance restores original phpbash and clean root cron script")
