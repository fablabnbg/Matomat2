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
		data=res.readall().decode('ascii')
		if res.status==request.http.client.OK:
			data=json.loads(data)
		return res.status,data

	def change_auth(self,password=None,public_key=None):
		data={'username':self.username,'password':password,'public_key':public_key}
		jdata=json.dumps(data)
		return self.query('user',post_data=jdata)

	def lookup(self,key):
		status,resp=self.query('user',get_data={'key':key})
		if status!=request.http.client.OK:
			return []
		return resp['username']

	def get_items(self):
		return self.query('items')

	def get_date(self):
		data=self.query('date')
		return dateutil.parser.parse(data['date'])

	def balance(self):
		return self.query('balance')

	def pay(self,amount):
		return self.query('pay',post_data=json.dumps(amount))

	def buy(self,item_id):
		return self.query('buy',post_data=json.dumps(item_id))

