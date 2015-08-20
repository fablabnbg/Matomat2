import urllib.request
import ssl
import inspect

def urlopen(req,cert):
	args=inspect.getfullargspec(urllib.request.urlopen)
	if not 'context' in args.args+args.kwonlyargs: #if urlopen has no context argument we monkey patch the SSLContext construction
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

