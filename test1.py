import os
import random
import StringIO
import time
import pycurl

times = [1.83, 4.18, 1.88, 5.19, 5.32, 3.94, 1.81, 1.89, 1.85, 1.5]
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

def query(url):
	output = StringIO.StringIO()

	query = pycurl.Curl()
	query.setopt(pycurl.URL, url)
	
	try:
		query.perform()
		return output.getvalue()
	except pycurl.error as exc:
		raise ValueError("Unable to reach %s (%s)" % (url, exc))

for j in range(5):
	print j
	for i in  range(len(topsites)):
		start_time = time.time()
		check_page = query(topsites[i])
		tym = time.time() - start_time
		times[i] = (times[i] + tym) / 2

print times