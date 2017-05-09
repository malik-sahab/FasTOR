import os
import time
import requests
import networkx as nx
import statistics

from geoip import geolite2
from math import cos, sqrt, asin
from stem.control import Controller
from stem.descriptor import parse_file


# 1. A library that holds 35 nodes that have been initialized with lat and lon positions
allNodes = {
            # south and central america
            'SA1':{'relays':[], 'lat':-21.9, 'lon':-57.3, 'bndw':[], 'avbndw':0}, 'CA1':{'relays':[], 'lat':17, 'lon':-72.9, 'bndw':[], 'avbndw':0},
            # north america
            'NA1':{'relays':[], 'lat':50.25, 'lon':-126.3, 'bndw':[], 'avbndw':0}, 'NA2':{'relays':[], 'lat':50.25, 'lon':-113.9, 'bndw':[], 'avbndw':0},
            'NA3':{'relays':[], 'lat':50.25, 'lon':-101.5, 'bndw':[], 'avbndw':0}, 'NA4':{'relays':[], 'lat':50.25, 'lon':-89.1, 'bndw':[], 'avbndw':0},
            'NA5':{'relays':[], 'lat':50.25, 'lon':-76.7, 'bndw':[], 'avbndw':0}, 'NA6':{'relays':[], 'lat':50.25, 'lon':-64.3, 'bndw':[], 'avbndw':0},
            'NA7':{'relays':[], 'lat':39, 'lon':-126.3, 'bndw':[], 'avbndw':0}, 'NA8':{'relays':[], 'lat':39, 'lon':-113.9, 'bndw':[], 'avbndw':0},
            'NA9':{'relays':[], 'lat':39, 'lon':-101.5, 'bndw':[], 'avbndw':0}, 'NA10':{'relays':[], 'lat':39, 'lon':-89.1, 'bndw':[], 'avbndw':0},
            'NA11':{'relays':[], 'lat':39, 'lon':-76.7, 'bndw':[], 'avbndw':0}, 'NA12':{'relays':[], 'lat':39, 'lon':-64.3, 'bndw':[], 'avbndw':0},
            # africa
            'AF1':{'relays':[], 'lat':12.23, 'lon':-5.27, 'bndw':[], 'avbndw':0},'AF2':{'relays':[], 'lat':-23.9, 'lon':23.9, 'bndw':[], 'avbndw':0}, 
            'AF3':{'relays':[], 'lat':-4.2, 'lon':56.3, 'bndw':[], 'avbndw':0},
             # asia
            'AS1':{'relays':[], 'lat':22.6, 'lon':75.1, 'bndw':[], 'avbndw':0},'AS2':{'relays':[], 'lat':7.1, 'lon':102.5, 'bndw':[], 'avbndw':0}, 
            'AS3':{'relays':[], 'lat':26.9, 'lon':120.1, 'bndw':[], 'avbndw':0},'AS4':{'relays':[], 'lat':42, 'lon':135.5, 'bndw':[], 'avbndw':0},
            # australia
            'AU1':{'relays':[], 'lat':-35.2, 'lon':157.1, 'bndw':[], 'avbndw':0}, 
            # europe
            'EU1':{'relays':[], 'lat':64.9, 'lon':-17.9, 'bndw':[], 'avbndw':0}, 'EU2':{'relays':[], 'lat':64.7, 'lon':15.2, 'bndw':[], 'avbndw':0}, 
            'EU3':{'relays':[], 'lat':64.7, 'lon':27.7, 'bndw':[], 'avbndw':0}, 'EU4':{'relays':[], 'lat':56.2, 'lon':12.67, 'bndw':[], 'avbndw':0},
            'EU5':{'relays':[], 'lat':56.2, 'lon':24.67, 'bndw':[], 'avbndw':0}, 'EU6':{'relays':[], 'lat':56.2, 'lon':36.67, 'bndw':[], 'avbndw':0},
            'EU7':{'relays':[], 'lat':47.8, 'lon':-4, 'bndw':[], 'avbndw':0}, 'EU8':{'relays':[], 'lat':47.8, 'lon':8.8, 'bndw':[], 'avbndw':0},
            'EU9':{'relays':[], 'lat':47.8, 'lon':21.5, 'bndw':[], 'avbndw':0}, 'EU10':{'relays':[], 'lat':47.8, 'lon':34.2, 'bndw':[], 'avbndw':0},
            'EU11':{'relays':[], 'lat':39.2, 'lon':-5, 'bndw':[], 'avbndw':0}, 'EU12':{'relays':[], 'lat':39.2, 'lon':6.15, 'bndw':[], 'avbndw':0},
            'EU13':{'relays':[], 'lat':39.2, 'lon':17.25, 'bndw':[], 'avbndw':0}
            }

def getavbndw():
	for n in allNodes:
		if len(allNodes[n]['bndw']): 
			allNodes[n]['avbndw'] = statistics.median(allNodes[n]['bndw'])

def calDistance(lat1, lon1, lat2, lon2): #Haversine formula
  p = 0.0175
  a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
  return 12700 * asin(sqrt(a)) 

def getIpLocation(rel):
  ip = rel.address
  # print ip
  loc = geolite2.lookup(ip)
  # print loc
  if (loc != None):
    if loc.location != None:
      lat = loc.location[0]
      lon = loc.location[1]
      classifyNodes(rel, lat, lon)

def classifyNodes(rel, lat, lon):
  if (lat < -2): # south
    if (lon < -32):
      allNodes['SA1']['relays'].append(rel)
      allNodes['SA1']['bndw'].append(rel.bandwidth)
    elif (lon < 45):
      allNodes['AF2']['relays'].append(rel)
      allNodes['AF2']['bndw'].append(rel.bandwidth)
    elif (lon < 75):
      allNodes['AF3']['relays'].append(rel)
      allNodes['AF3']['bndw'].append(rel.bandwidth)
    else:
      allNodes['AU1']['relays'].append(rel)
      allNodes['AU1']['bndw'].append(rel.bandwidth)
  elif (lat < 27): # centre
    if (lon < -52):
      allNodes['CA1']['relays'].append(rel)
      allNodes['CA1']['bndw'].append(rel.bandwidth)
    elif (lon < -25):
      allNodes['AF1']['relays'].append(rel)
      allNodes['AF1']['bndw'].append(rel.bandwidth)
    elif (lon < 90):
      allNodes['AS1']['relays'].append(rel)
      allNodes['AS1']['bndw'].append(rel.bandwidth)
    elif (lon < 110):
      allNodes['AS2']['relays'].append(rel)
      allNodes['AS2']['bndw'].append(rel.bandwidth)
    else:
      allNodes['AS3']['relays'].append(rel)
      allNodes['AS3']['bndw'].append(rel.bandwidth)
  else: # north
    if (lon < -38):
      if (lat < 45): # lower north
        if (lon < -120.1):
          allNodes['NA7']['relays'].append(rel)
          allNodes['NA7']['bndw'].append(rel.bandwidth)
        elif (lon < -107.7):
          allNodes['NA8']['relays'].append(rel)
          allNodes['NA8']['bndw'].append(rel.bandwidth)
        elif (lon < -95.3):
          allNodes['NA9']['relays'].append(rel)
          allNodes['NA9']['bndw'].append(rel.bandwidth)
        elif (lon < -82.9):
          allNodes['NA10']['relays'].append(rel)
          allNodes['NA10']['bndw'].append(rel.bandwidth)
        elif (lon < -70.5):
          allNodes['NA11']['relays'].append(rel)
          allNodes['NA11']['bndw'].append(rel.bandwidth)
        else:
          allNodes['NA12']['relays'].append(rel)
          allNodes['NA12']['bndw'].append(rel.bandwidth)
      else: # upper north
        if (lon < -120.1):
          allNodes['NA1']['relays'].append(rel)
          allNodes['NA1']['bndw'].append(rel.bandwidth)
        elif (lon < -107.7):
          allNodes['NA2']['relays'].append(rel)
          allNodes['NA2']['bndw'].append(rel.bandwidth)
        elif (lon < -95.3):
          allNodes['NA3']['relays'].append(rel)
          allNodes['NA3']['bndw'].append(rel.bandwidth)
        elif (lon < -82.9):
          allNodes['NA4']['relays'].append(rel)
          allNodes['NA4']['bndw'].append(rel.bandwidth)
        elif (lon < -70.5):
          allNodes['NA5']['relays'].append(rel)
          allNodes['NA5']['bndw'].append(rel.bandwidth)
        else:
          allNodes['NA6']['relays'].append(rel)
          allNodes['NA6']['bndw'].append(rel.bandwidth)
    elif (lon > 80):
      allNodes['AS4']['relays'].append(rel)
      allNodes['AS4']['bndw'].append(rel.bandwidth)
    else:
      if (lon < -10):
        allNodes['EU1']['relays'].append(rel)
        allNodes['EU1']['bndw'].append(rel.bandwidth)
      elif (lat > 60.5):
        if (lon < 21.5):
          allNodes['EU2']['relays'].append(rel)
          allNodes['EU2']['bndw'].append(rel.bandwidth)
        else:
          allNodes['EU3']['relays'].append(rel)
          allNodes['EU3']['bndw'].append(rel.bandwidth)
      elif (lat > 52):
        if (lon < 18.7):
          allNodes['EU4']['relays'].append(rel)
          allNodes['EU4']['bndw'].append(rel.bandwidth)
        elif (lon < 30.7):
          allNodes['EU5']['relays'].append(rel)
          allNodes['EU5']['bndw'].append(rel.bandwidth)
        else:
          allNodes['EU6']['relays'].append(rel)
          allNodes['EU6']['bndw'].append(rel.bandwidth)
      elif (lat > 43.6):
        if (lon < 2.4):
          allNodes['EU7']['relays'].append(rel)
          allNodes['EU7']['bndw'].append(rel.bandwidth)
        elif (lon < 15.2):
          allNodes['EU8']['relays'].append(rel)
          allNodes['EU8']['bndw'].append(rel.bandwidth)
        elif (lon < 28):
          allNodes['EU9']['relays'].append(rel)
          allNodes['EU9']['bndw'].append(rel.bandwidth)
        else:
          allNodes['EU10']['relays'].append(rel)
          allNodes['EU10']['bndw'].append(rel.bandwidth)
      else:
        if (lon < 0.6):
          allNodes['EU11']['relays'].append(rel)
          allNodes['EU11']['bndw'].append(rel.bandwidth)
        elif (lon < 11.8):
          allNodes['EU12']['relays'].append(rel)
          allNodes['EU12']['bndw'].append(rel.bandwidth)
        else: 
          allNodes['EU13']['relays'].append(rel)
          allNodes['EU13']['bndw'].append(rel.bandwidth)
        
with Controller.from_port(port = 9051) as controller:
  controller.authenticate()
  data_dir = controller.get_conf('DataDirectory')
  # 2. Using descriptors to get the list of relays
  
  res = requests.get('http://www.google.com')
  resTime = res.elapsed.total_seconds()
  print resTime

  t0 = time.time()
  for rel in parse_file(os.path.join(data_dir, 'cached-microdesc-consensus')):
    # 2a. Get the ip location
    if (rel is not None):
      getIpLocation(rel)
  getavbndw()
  t1 = time.time()
  print t1 - t0
  for i in allNodes:
  	print allNodes[i]
  
  G = nx.Graph()
  for n in allNodes:
  	for m in allNodes:
  		dist = calDistance(allNodes[n]['lat'], allNodes[n]['lon'], allNodes[m]['lat'], allNodes[m]['lon'])
  		G.add_edge(n, m, distance=dist)

  for (u,v,d) in G.edges(data='distance'):
  	print u, v, d
  # print "Graph nodes: ", G.nodes()
  # print "Graph edges: ", G.edges()
  
  #suppose we want to establish a circuit between AS1 and EU1
  shortpath = nx.dijkstra_path(G,'AS1','EU1', weight='distance')
  print "shortest path: ", shortpath

