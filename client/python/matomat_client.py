from urllib import request, parse
import json
import dateutil.parser

class Matomat_client:
	def __init__(self,addr):
		self.addr=addr
		self.username=None
		self.password=None

	def query(self,endpoint,get_data=None,post_data=None):
		url=self.addr+'api/'
		if not self.username is None:
			url+=self.username+'/'
		url+=endpoint
		if not get_data is None:
			url+='?'+parse.urlencode(get_data)
		headers=dict()
		if not self.password is None:
			headers['pass']=self.password
		req=request.Request(url,headers=headers)
		res=request.urlopen(req)
		data=None
		if res.status==request.http.client.OK:
			data=json.loads(res.readall().decode('ascii'))
		return data

	def lookup(self,key):
		return self.query('user',{'key':key})

	def get_items(self):
		return self.query('items')

	def get_date(self):
		data=self.query('date')
		return dateutil.parser.parse(data['date'])

