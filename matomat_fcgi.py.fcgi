#!/usr/bin/env python3
from flipflop import WSGIServer
from matomat_wsgi import application_single_db

if __name__=='__main__':
	WSGIServer(application_single_db()).run()
