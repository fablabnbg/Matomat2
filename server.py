#!/usr/bin/env python3
from wsgiref.simple_server import make_server
from wsgiref.util import shift_path_info
import matomat_wsgi
import os

try:
	fnfError=FileNotFoundError
except NameError:
	fnfError=IOError

def strip_app(environ,start_response):
	if environ['PATH_INFO']=='/':
		environ['PATH_INFO']='/index.html'
	if environ['PATH_INFO'].startswith('/api'):
		shift_path_info(environ)
	else:
		try:
			filename=os.path.join(os.getcwd(),'client','html',environ['PATH_INFO'][1:])
			f=open(filename,'rb')
		except fnfError:
			start_response("404 NOT FOUND",[])
			return []
		start_response("200 OK",[])
		return f
	return matomat_wsgi.application(environ,start_response)

if __name__=='__main__':
	s = make_server('', 8002, strip_app)
	s.serve_forever()
