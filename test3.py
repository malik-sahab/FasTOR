import os
import time
import requests
import networkx as nx
import statistics
import random
import pycurl
import StringIO
import stem.control

from geoip import geolite2
from math import cos, sqrt, asin
from stem.control import Controller
from stem.descriptor import parse_file

GUARD_RELAY = '9EA4649400C7D35E20C734FA737CF615E925F1E4'
MID_RELAY = ''
EXIT_RELAY = ''

relays = []
times = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
topsites = [
	'https://www.google.com.pk/',
	'https://www.youtube.com/',
	'https://www.apple.com/',
	'https://www.yahoo.com/',
	'https://www.linkedin.com/',
	'https://www.wikipedia.org/',
	'https://www.amazon.com/',
	'https://twitter.com',
	'https://www.pinterest.com',
	'https://www.quora.com'
	]

SOCKS_PORT = 9050
CONNECTION_TIMEOUT = 30

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

def getExit(rlist):
	flag = 0
	rel = ''
	frel = ''
	while (flag == 0):
		rel = random.choice(rlist)
		if 'Exit' in rel.flags:
			frel = rel
			flag = 1
		else:
			flag = 0
	print "exit: " , frel.bandwidth
	return frel.fingerprint

def query(url):
	output = StringIO.StringIO()

	query = pycurl.Curl()
	query.setopt(pycurl.URL, url)
	query.setopt(pycurl.PROXY, 'localhost')
	query.setopt(pycurl.PROXYPORT, SOCKS_PORT)
	query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)
	query.setopt(pycurl.CONNECTTIMEOUT, CONNECTION_TIMEOUT)
	query.setopt(pycurl.WRITEFUNCTION, output.write)

	try:
		query.perform()
		#print output.getvalue()
		return output.getvalue()
	except pycurl.error as exc:
		raise ValueError("Unable to reach %s (%s)" % (url, exc))


def scan(controller, path):

	circuit_id = controller.new_circuit(path, await_build = True)

	def attach_stream(stream):
		if stream.status == 'NEW':
			controller.attach_stream(stream.id, circuit_id)

	controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)

	try:
		controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us

		#for i in  range(len(topsites)):
		start_time = time.time()
		check_page = query('https://www.google.com.pk/')
		tym = time.time() - start_time
		print tym
		#times[i] = tym

	finally:
		controller.remove_event_listener(attach_stream)
		controller.reset_conf('__LeaveStreamsUnattached')

def getavbndw():
	for n in allNodes:
		if len(allNodes[n]['bndw']): 
			allNodes[n]['avbndw'] = statistics.median(allNodes[n]['bndw'])

def calDistance(lat1, lon1, lat2, lon2): #Haversine formula
	p = 0.0175
	a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
	return 12700 * asin(sqrt(a)) 

def getDistance(G, start, end): #Distance from one node to another
	filt = list(filter(lambda (a, b, c): (a == start and b == end) or (a == end and b == start), G.edges(data='distance')))
	return filt[0][2]

def shortestpath(G, start, end): #Shortest Path of length three
	#print G.edges(data='distance')
	filt1 = list(filter(lambda (a, b, c): a == start, G.edges(data='distance')))
	filt2 = list(filter(lambda (a, b, c): b == start, G.edges(data='distance')))
	filt1 = list(filter(lambda (a, b, c): a != start or b != start, filt1))
	filt2 = list(filter(lambda (a, b, c): a != start or b != start, filt2))
	path = []
	a = ''
	for i, _ in enumerate(filt2):
		lst = list(filt2[i])
		a = lst[0]
		lst[0] = start
		lst[1] = a
		filt2[i] = tuple(lst)
	filt = filt1 + filt2

	#getDistance(G, start, end)
	for i, _ in enumerate(filt):
		lst = list(filt[i])
		d = getDistance(G, lst[1], end)
		totald = d + lst[2]
		lst[2] = end
		lst.append(totald)
		filt[i] = tuple(lst)

	filt = list(filter(lambda (a, b, c, d): b != a and b != c, filt))
	mindist = 999999999999999
	node = ()
	for (a, b, c, d) in filt:
		if d < mindist:
			mindist = d
			node = (a, b, c, d)
	return node 
		
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
				
with Controller.from_port() as controller:
	controller.authenticate()
	data_dir = controller.get_conf('DataDirectory')
	# 2. Using descriptors to get the list of relays
	
	for rel in parse_file(os.path.join(data_dir, 'cached-microdesc-consensus')):
		# 2a. Get the ip location
		if (rel is not None):
			getIpLocation(rel) #2b. Append them into dictionary
	getavbndw()

	'''
	checklist = []
	for r in allNodes['EU4']['relays']:
		checklist.append(r.fingerprint)
	print ('9EA4649400C7D35E20C734FA737CF615E925F1E4' in checklist)
	'''
	G = nx.Graph()
	for n in allNodes:
		for m in allNodes:
			dist = calDistance(allNodes[n]['lat'], allNodes[n]['lon'], allNodes[m]['lat'], allNodes[m]['lon'])
			G.add_edge(n, m, distance=dist)

	shortpath = shortestpath(G, 'NA1', 'EU4')
	print "Shortest path: ", shortpath
	while(1):

		MID_RELAY = (random.choice(allNodes[shortpath[1]]['relays']))
		print "mid: " , MID_RELAY.bandwidth
		EXIT_RELAY = getExit(allNodes[shortpath[2]]['relays'])

		#print "GUARD_RELAY: ", GUARD_RELAY
		#print "MID_RELAY: ", MID_RELAY
		#print "EXIT_RELAY: ", EXIT_RELAY

		try:
			scan(controller, [GUARD_RELAY, MID_RELAY.fingerprint, EXIT_RELAY])
		except Exception as exc:
			print('=> %s' % (exc))

	#print "Times: ", times
	