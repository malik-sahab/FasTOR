import requests
import matplotlib.pyplot as plt

response = []
x = [1,2,3,4,5,6,7,8,9,10]

topsites = [
	'http://www.google.com',
	'http://youtube.com',
	'http://facebook.com',
	'http://baidu.com',
	'http://www.yahoo.com',
	'http://reddit.com',
	'http://wikipedia.org',
	'http://amazon.com',
	'http://tmall.com',
	'http://twitter.com']

for t in topsites:
	res = requests.get('http://www.google.com')
	time = res.elapsed.total_seconds()
	response.append(time)

f = open('data1.txt', 'w')
f.write(str(response))
f.close
