import wsgiref.handlers, datetime, os, re

from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template

from BeautifulSoup import BeautifulSoup

try:
	import simplejson
except ImportError:
	from django.utils import simplejson

class MainHandler(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		context = {}
		self.response.out.write(template.render(path, context))

class PageResults(webapp.RequestHandler):
	def get(self):
		url = self.request.get("url", default_value='http://google.com/')
		
		try:
			result = urlfetch.fetch(url)
			
			if result.status_code == 200:
				soup = BeautifulSoup(result.content)
			
			json = {
				'title': soup.head.title.string,
				'url': url,
			}
			
			try:
				json.update({'keywords': soup.head.find('meta', { 'name': 'keywords' })['content'].split(',')})
			except:
				json.update({'keywords': []})
			
			try:
				json.update({'description': soup.head.find('meta', { 'name': 'description' })['content']})
			except:
				json.update({'description': None})
			
			try:
				json.update({'author': soup.head.find('meta', { 'name': 'author' })['content']})
			except:
				json.update({'author': None})
			
			tags = soup.findAll(attrs={ 'rel': re.compile('^tag.*') })
			for tag in tags:
				json['keywords'] += [tag.string,]
			
			expires_date = datetime.datetime.utcnow() + datetime.timedelta(10)
			expires_str = expires_date.strftime("%d %b %Y %H:%M:%S GMT")
			self.response.headers.add_header("Expires", expires_str)
			self.response.out.write(simplejson.dumps(json))
		except urlfetch.InvalidURLError:
			self.error(500)

def main():
	urls = [
		('/', MainHandler),
		('/result', PageResults)
	]
	application = webapp.WSGIApplication(urls, debug=True)
	wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
	main()