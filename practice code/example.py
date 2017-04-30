import re
import json
from urllib2 import urlopen
from stem import CircStatus
from stem.control import Controller

def getIpLocation(ip):
	
	if (ip != 'unknown') : 
		url = 'https://ipinfo.io/' + ip + '/json'
		response = urlopen(url)
		data = json.load(response)
		#print (data['city'], data['country'])

if __name__ == '__main__':

	with Controller.from_port(port = 9051) as controller:
  		controller.authenticate()  # provide the password here if you set one

  		for circ in sorted(controller.get_circuits()):
	  		if circ.status != CircStatus.BUILT:
	  			continue
	  		print ("")
	  		print ("Circuit ", circ.id, circ.purpose)

	  		for i, entry in enumerate(circ.path):
	  			div = '+' if (i == len(circ.path) - 1) else '|'
	  			fingerprint, nickname = entry

	  			desc = controller.get_network_status(fingerprint, None)
	  			address = desc.address if desc else 'unknown'
				getIpLocation(address)
				print(" %s- %s (%s, %s)" % (div, fingerprint, nickname, address))
