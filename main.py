import webapp2
from google.appengine.api import urlfetch
# from google.appengine.api import memcache
import re
import time
import random
from product import pids
import urllib
import json
from pyquery import PyQuery
from lxml import etree



VERIFIEDPATTERN = re.compile(r'Verified Purchase')
VOTEPATTERN = re.compile(r'(person)|(people) found this helpful')


#54.239.26.128
IPADRESS = ["54.239.25.200", "54.239.25.192", "54.239.17.7", "54.239.26.128", "54.239.17.7", "54.239.26.128", "54.239.25.208"]
REVIEW_URL = "http://{0}/product-reviews/{1}/?ie=UTF8&filterByStar=all_stars&pageNumber={2}&pageSize=50&sortBy=helpful"


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!!!')

class ReviewHandler(webapp2.RequestHandler):
	def get(self):
		self.response.write("pls use post method")
	def post(self):
		"""
		payload = {
			"startNum": int,
			"number": int,
		}
		"""
		#store post para
		startPoint = self.request.get("startpoint")
		steps = self.request.get("steps")

		#read file & combine query
		links = []

		product_ids = pids
		for id in product_ids:
			ip = self.random_ip(IPADRESS)
			links.append(REVIEW_URL.format(ip, id, 1))

		#filter
		links = links[int (startPoint) - 1:]
		links = links[:int(steps)]
		# self.response.write(json.dumps(links))
		print "links:%s" % links
		#fetch (loop)
		htmls = map(self.getReview, links)
		# result = dict(zip(links, map(self.getReview, links)))
		# results = map(self.parseReview, links)
		results = map(self.parseReview, htmls)
		self.response.write(json.dumps(dict(zip(links, results))))
		# self.response.write(json.dumps(results))


	def getReview(self, url):
		# random sleep for avoiding spider detection
		timeToSleep = float(random.randint(15, 50)) / 25
		time.sleep(timeToSleep)

		result = urlfetch.fetch(url)
		print(result)
		if(len(result.content) == 1378):
			return False
		return result.content

	def random_ip(self, ips):
		#generate random ip
		return ips[random.randint(0, len(ips) - 1)]
	# def decode(self, url):
	# 	return url.decode('utf8') 

	def parseReview(self, html):
		# html = html.replace("<!doctype html>", "")
		# print(html)
		# print(len(html))
		# html = html.replace(" ","")
		# print(len(html))
		print(html)
		# pq = PyQuery(url = url)
		pq = PyQuery(html)
		# print(pq)
		# total_page = pq(".page-button").eq(-1).text()

		review={}

		review["author"] = [i.text() for i in pq(".reviews-content .author").items("a")]
		review["rate"] = map(lambda i: i[0], [i.text() for i in pq(".reviews-content .review-rating").items('span')])
		review["title"] = [i.text() for i in pq(".reviews-content .review-title").items("a")]
		review["content"] = [i.text() for i in pq(".reviews-content .a-size-base.review-text").items("span")]
		review["date"] = [i.text() for i in pq(".reviews-content .review-date").items("span")]
		review["verified"] = map(self.isVerified, [i.text() for i in pq(".reviews-content .a-row.a-spacing-mini.review-data").items("div")])
		review["color"] = [i.text() for i in pq(".reviews-content .review-data .a-link-normal.a-color-secondary").items("a")]
		review["vote"] = map(self.numVote, [i.text() for i in pq(".reviews-content span.cr-vote-buttons").items()])
		print(review)
		return review
	
	def isVerified(slef, words):
		if VERIFIEDPATTERN.findall(words):
			return 1
		else:
			return 0

	def numVote(self, words):
		if VOTEPATTERN.search(words):
			num = words.split()[0]
			if num == "One":
				num = 1
		else:
			num = 0
		return int(num)

class TestHandler(webapp2.RequestHandler):
	def get(self):
		# x="https://www.googleapis.com/storage/v1/b?project=my-amazon-project"
		# result = urlfetch.fetch(x)
		self.response.write(self.test(pids))
		# self.response.write("test sucess")
	def test(self, pids):
		return len(pids)

# class CacheHandler(webapp2.RequestHandler):
	# def get(self):
		# self.response.write("cache")
	# def get_data():
	# 	if data is not None:
	# 		return data
	# 	else:
	# 		data = self.query_for_data()
	# 		memcache.add()

app = webapp2.WSGIApplication([
    (r'/', MainPage),
    (r'/reviews', ReviewHandler),
    (r'/test', TestHandler),
    # ('/cache', CacheHandler)
], debug=True)

#update: $ gcloud preview app deploy app.yaml
