import GeoIP
import os
import requests

from stem.control import Controller
from stem.descriptor import parse_file

def getIpLocation(ip): 
    gi = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
    gir = gi.country_name_by_addr(ip)
    return gir
    
with Controller.from_port(port = 9051) as controller:
  controller.authenticate()

  res = requests.get('http://www.google.com')
  time = res.elapsed.total_seconds()
  print (time)

  data_dir = controller.get_conf('DataDirectory')
  
"""
  print 'Relays:'

  for rel in parse_file(os.path.join(data_dir, 'cached-microdesc-consensus')):
    loc = getIpLocation(rel.address)
    print '  %s (%s, %s)' % (rel.nickname, rel.address, loc)

"""