import json
import hmac
from hashlib import sha256
from datetime import datetime
from pytz import utc
from urllib.request import urlopen
from urllib.parse import urlencode
import ssl

class SysE(object):
	def __init__(self,url,clientid,key):
		self.url=url
		self.clientid=clientid
		self.key=bytes(key)

	def do_communication(self,data):
		response=urlopen(self.url,data=urlencode(data).encode('ascii'),context=ssl.create_default_context())
		res=200<=response.status<300
		response.close()
		return res

	def debit(self,account_id,amount,reference):
		body={'bpid':int(account_id),'amount':int(amount),'batchbook':True,'reference':reference}
		data={'id':0,'created_on':datetime.now(utc).isoformat(),'type':'directdebitreq','body':body}
		jsondata=json.dumps(data)
		hmacdata=hmac.HMAC(self.key,jsondata.encode('utf8'),sha256).hexdigest()
		postdata={'clientid':self.clientid,'hmac':hmacdata,'data':jsondata}
		return self.do_communication(postdata)

