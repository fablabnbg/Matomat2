from urllib import request, parse
import json
import dateutil.parser
import checked_ssl
import ssl

class Matomat_client:
	def __init__(self,addr,cert=None):
		self.addr=addr
		self.username=None
		self.password=None
		if cert is None:
			self.cert=None
		elif type(cert)==bytes:
			self.cert=cert
		elif type(cert)==str:
			if cert.startswith('-----BEGIN CERTIFICATE-----'):
				self.cert=ssl.PEM_cert_to_DER_cert(cert)
			else:
				with open(cert,'rb') as f:
					cert=f.read()
				if cert.startswith(b'-----BEGIN CERTIFICATE-----'):
					cert=ssl.PEM_cert_to_DER_cert(cert.decode('ascii'))
				self.cert=cert
		else:
			raise ValueError('Unknown Certificate type')

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
		res=checked_ssl.urlopen(req,self.cert)
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
		status,res=self.query('items')
		if status!=200:
			return None
		return res

	def get_date(self):
		status,data=self.query('date')
		if status!=200:
			return None
		return dateutil.parser.parse(data['date'])

	def balance(self):
		status,res=self.query('balance')
		if status!=200:
			return None
		return res

	def pay(self,amount):
		return self.query('pay',post_data=json.dumps(amount))

	def buy(self,item_id):
		return self.query('buy',post_data=json.dumps(item_id))

	def undo(self):
		return self.query('undo',post_data=json.dumps('dummy'))

