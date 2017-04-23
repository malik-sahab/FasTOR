import GeoIP
import json
from stem import CircStatus
from stem.control import Controller

def getIpLocation(ip):
		gi = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
		#print gi.country_name_by_addr(ip)
		return gi.country_name_by_addr(ip)
		#print (data['city'], data['country'])

with Controller.from_port(port = 9051) as controller:
	controller.authenticate()  # provide the password here if you set one

	for circ in sorted(controller.get_circuits()):
		
		if circ.status != CircStatus.BUILT:
			continue
		
		print ("")
		print ("Circuit %s (%s)" % (circ.id, circ.fingerprint))

		for i, entry in enumerate(circ.path):
			div = '+' if (i == len(circ.path) - 1) else '|'
			fingerprint, nickname = entry

			desc = controller.get_network_status(fingerprint, None)
			address = desc.address if desc else 'unknown'

			loc = getIpLocation(address)
			print(" %s- %s (%s, %s)" % (div, nickname, address, loc))
