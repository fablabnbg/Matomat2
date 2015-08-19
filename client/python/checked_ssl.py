import urllib.request
import ssl

def urlopen(req,cert):
	if True: #TODO check if urlopen has context argument. Then no monkeypatch needed
		orig_context=ssl.SSLContext
		ssl.SSLContext=Checked_context_factory(cert)
		try:
			res=urllib.request.urlopen(req)
		finally:
			ssl.SSLContext=orig_context
	else:
		res=urllib.request.urlopen(req,context=Checked_context(ssl.PROTOCOL_SSLv23,cert=cert))
	return res


class Checked_context_factory:
	def __init__(self,cert):
		self.cert=cert

	def __call__(self,*args,**kwargs):
		return Checked_context(*args,cert=self.cert,**kwargs)
		

class Checked_context(ssl.SSLContext):
	def __init__(self,*args,cert,**kwargs):
		super().__init__(*args,**kwargs)
		self.cert=cert

	def wrap_socket(self,*args,**kwargs):
		sock=super().wrap_socket(*args,**kwargs)
		cert=sock.getpeercert(True)
		if not self.cert is None:
			if self.cert!=cert:
				raise ssl.CertificateError('Certificate is not equal to expected')
		return sock

