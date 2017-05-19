import os
import random
import StringIO
import time
import pycurl
import stem.control
from stem.descriptor import parse_file

GUARD_RELAY = '9EA4649400C7D35E20C734FA737CF615E925F1E4'
MID_RELAY = ''
EXIT_RELAY = ''

relays = []
times = [3.347, 8.457, 3.922, 4.005, 5.715, 4.114, 4.149, 8.329, 4.943, 4.158]
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
	print frel.flags
	return frel.fingerprint

def getMid(rlist):
	flag = 0
	rel = ''
	frel = ''
	while (flag == 0):
		rel = random.choice(rlist)
		if rel.bandwidth > 5000:
			frel = rel
			flag = 1
		else:
			flag = 0
	#print frel.flags
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

		for i in  range(len(topsites)):
			start_time = time.time()
			check_page = query(topsites[i])
			tym = time.time() - start_time
			print tym
			times[i] = (times[i] + tym) / 2

	finally:
		controller.remove_event_listener(attach_stream)
		controller.reset_conf('__LeaveStreamsUnattached')

with stem.control.Controller.from_port() as controller:
	controller.authenticate()
	data_dir = controller.get_conf('DataDirectory')
	for rel in parse_file(os.path.join(data_dir, 'cached-microdesc-consensus')):
		relays.append(rel)

	MID_RELAY = getMid(relays)
	#print MID_RELAY.flags
	EXIT_RELAY = getExit(relays)

	for i in range(5):
		try:
			scan(controller, [GUARD_RELAY, MID_RELAY, EXIT_RELAY])
		except Exception as exc:
			print('=> %s' % (exc))

print times