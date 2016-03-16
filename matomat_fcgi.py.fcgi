#!/usr/bin/env python3
from flipflop import WSGIServer
from matomat_wsgi import application

if __name__=='__main__':
	WSGIServer(application).run()
