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
		if isinstance(post_data,str):
			post_data=post_data.encode('ascii')
		req=request.Request(url,data=post_data,headers=headers)
		res=request.urlopen(req)
		data=None
		if res.status==request.http.client.OK:
			data=json.loads(res.readall().decode('ascii'))
		return data

	def change_auth(self,password=None,public_key=None):
		data={'username':self.username,'password':password,'public_key':public_key}
		jdata=json.dumps(data)
		return self.query('user',post_data=jdata)

	def lookup(self,key):
		return self.query('user',get_data={'key':key})

	def get_items(self):
		return self.query('items')

	def get_date(self):
		data=self.query('date')
		return dateutil.parser.parse(data['date'])

