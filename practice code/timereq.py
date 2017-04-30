import StringIO
import time

import pycurl

import stem.control

fingerprint = '07CB5C1E95678419E0A7ADE864A522941FA8144E'
rel2 = '81B75D534F91BFB7C57AB67DA10BCEF622582AE8'
EXIT_FINGERPRINT = '379FB450010D17078B3766C2273303C358C3A442'


times = []
topsites = [
	'http://www.google.com',
	'http://youtube.com',
	'http://facebook.com',
	'http://www.yahoo.com',
	'http://reddit.com',
	'http://wikipedia.org',
	'http://amazon.com',
	'http://twitter.com']

SOCKS_PORT = 9050
CONNECTION_TIMEOUT = 30

def query(url):
  """
  Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
  """

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
    return output.getvalue()
  except pycurl.error as exc:
    raise ValueError("Unable to reach %s (%s)" % (url, exc))


def scan(controller, path):
  """
  Fetch check.torproject.org through the given path of relays, providing back
  the time it took.
  """

  circuit_id = controller.new_circuit(path, await_build = True)

  def attach_stream(stream):
    if stream.status == 'NEW':
      controller.attach_stream(stream.id, circuit_id)

  controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)

  try:
    controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us
    start_time = time.time()

    for t in topsites:
    	check_page = query(t)
    	times.append(time.time() - start_time)

  finally:
    controller.remove_event_listener(attach_stream)
    controller.reset_conf('__LeaveStreamsUnattached')

with stem.control.Controller.from_port() as controller:
	controller.authenticate()
	try:
		scan(controller, [fingerprint, rel2, EXIT_FINGERPRINT])
		f = open('data2.txt', 'w')
		f.write(str(times))
		f.close
	except Exception as exc:
	  print('%s => %s' % (fingerprint, exc))