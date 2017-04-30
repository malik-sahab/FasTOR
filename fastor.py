import GeoIP
import os
import requests

from stem.control import Controller
from stem.descriptor import parse_file

# 1. A library that holds 35 nodes that have been initialized with lat and lon positions
allNodes = {
            # south and central america
            'SA1':{'relays':[], 'lat':-21.9, 'lon':-57.3, 'bndw':0}, 'CA1':{'relays':[], 'lat':17, 'lon':-72.9, 'bndw':0},
            # north america
            'NA1':{'relays':[], 'lat':50.25, 'lon':-126.3, 'bndw':0}, 'NA2':{'relays':[], 'lat':50.25, 'lon':-113.9, 'bndw':0},
            'NA3':{'relays':[], 'lat':50.25, 'lon':-101.5, 'bndw':0}, 'NA4':{'relays':[], 'lat':50.25, 'lon':-89.1, 'bndw':0},
            'NA5':{'relays':[], 'lat':50.25, 'lon':-76.7, 'bndw':0}, 'NA6':{'relays':[], 'lat':50.25, 'lon':-64.3, 'bndw':0},
            'NA7':{'relays':[], 'lat':39, 'lon':-126.3, 'bndw':0}, 'NA8':{'relays':[], 'lat':39, 'lon':-113.9, 'bndw':0},
            'NA9':{'relays':[], 'lat':39, 'lon':-101.5, 'bndw':0}, 'NA10':{'relays':[], 'lat':39, 'lon':-89.1, 'bndw':0},
            'NA11':{'relays':[], 'lat':39, 'lon':-76.7, 'bndw':0}, 'NA12':{'relays':[], 'lat':39, 'lon':-64.3, 'bndw':0},
            # africa
            'AF1':{'relays':[], 'lat':12.23, 'lon':-5.27, 'bndw':0},'AF2':{'relays':[], 'lat':-23.9, 'lon':23.9, 'bndw':0}, 
            'AF3':{'relays':[], 'lat':-4.2, 'lon':56.3, 'bndw':0},
             # asia
            'AS1':{'relays':[], 'lat':22.6, 'lon':75.1, 'bndw':0},'AS2':{'relays':[], 'lat':7.1, 'lon':102.5, 'bndw':0}, 
            'AS3':{'relays':[], 'lat':26.9, 'lon':120.1, 'bndw':0},'AS4':{'relays':[], 'lat':42, 'lon':135.5, 'bndw':0},
            # australia
            'AU1':{'relays':[], 'lat':-35.2, 'lon':157.1, 'bndw':0}, 
            # europe
            'EU1':{'relays':[], 'lat':64.9, 'lon':-17.9, 'bndw':0}, 'EU2':{'relays':[], 'lat':64.7, 'lon':15.2, 'bndw':0}, 
            'EU3':{'relays':[], 'lat':64.7, 'lon':27.7, 'bndw':0}, 'EU4':{'relays':[], 'lat':56.2, 'lon':12.67, 'bndw':0},
            'EU5':{'relays':[], 'lat':56.2, 'lon':24.67, 'bndw':0}, 'EU6':{'relays':[], 'lat':56.2, 'lon':36.67, 'bndw':0},
            'EU7':{'relays':[], 'lat':47.8, 'lon':-4, 'bndw':0}, 'EU8':{'relays':[], 'lat':47.8, 'lon':8.8, 'bndw':0},
            'EU9':{'relays':[], 'lat':47.8, 'lon':21.5, 'bndw':0}, 'EU10':{'relays':[], 'lat':47.8, 'lon':34.2, 'bndw':0},
            'EU11':{'relays':[], 'lat':39.2, 'lon':-5, 'bndw':0}, 'EU12':{'relays':[], 'lat':39.2, 'lon':6.15, 'bndw':0},
            'EU13':{'relays':[], 'lat':39.2, 'lon':17.25, 'bndw':0}
            }

def getIpLocation(rel):
    ip = rel.address 
    gi = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
    gir = gi.country_name_by_addr(ip)
    #lat = ...
    #lon = ...
    classifyNodes(rel, lat, lon)
 
def classifyNodes(rel, lat, lon):
  if (lat < -2): # south
    if (lon < -32):
      allNodes['SA1']['relays'].append(rel)
    elif (lon < 45):
      allNodes['AF2']['relays'].append(rel)
    elif (lon < 75):
      allNodes['AF3']['relays'].append(rel)
    else:
      allNodes['AU1']['relays'].append(rel)
  elif (lat < 27): # centre
    if (lon < -52):
      allNodes['CA1']['relays'].append(rel)
    elif (lon < -25):
      allNodes['AF1']['relays'].append(rel)
    elif (lon < 90):
      allNodes['AS1']['relays'].append(rel)
    elif (lon < 110):
      allNodes['AS2']['relays'].append(rel)
    else:
      allNodes['AS3']['relays'].append(rel)  
  else:
    
with Controller.from_port(port = 9051) as controller:
  controller.authenticate()

  res = requests.get('http://www.google.com')
  time = res.elapsed.total_seconds()
  print (time)

  data_dir = controller.get_conf('DataDirectory')
  
"""
  print 'Relays:'

  for rel in parse_file(os.path.join(data_dir, 'cached-microdesc-consensus')):
    getIpLocation(rel)
    print '  %s (%s, %s)' % (rel.nickname, rel.address, loc)

"""