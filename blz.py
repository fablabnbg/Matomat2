import struct

def check_iban(iban):
	if iban[:2].upper()!='DE':
		raise ValueError('Only german IBANs are supported')
	r=str(98-int(iban[4:]+'131400')%97)
	if len(r)<2:
		r='0'+r
	return iban[2:4]==r


def from_iban(iban):
	if iban[:2].upper()!='DE':
		raise ValueError('Only german IBANs are supported')
	blz=iban[4:12]
	return blz

class BLZfile(object):
	def __init__(self, filename):
		self.cache=dict()
		self.filename=filename
	def __getitem__(self, blz):
		blz=str(blz)
		try:
			res=self.cache[blz]
		except KeyError:
			res=self.lookup(blz)
		return res
	
	def lookup(self, blz):
		with open(self.filename,'rb') as f:
			num_records=f.seek(0,2)//BLZrecord.size
			upper=num_records
			lower=0
			while upper-lower>1:
				idx=f.seek((lower+upper)//2)
				f.seek(idx*BLZrecord.size)
				r=BLZrecord(f.read(BLZrecord.size))
				if r.blz==blz:
					self.cache[blz]=r
					return r
				if r.blz<blz:
					lower=idx
				else:
					upper=idx
			raise RuntimeError('BLZ "{}" does not exist'.format(blz))


class BLZrecord(object):
	fmt='8s1s58s5s35s27s5s11s2s6s1s1s8s2x'
	size=struct.calcsize(fmt)
	def __init__(self, data):
		data=struct.unpack(self.fmt,data)
		self.blz=data[0].decode('ascii')
		self.leading=data[1]==b'1'
		self.name=data[2].decode('cp1252')
		self.plz=data[3].decode('ascii')
		self.city=data[4]
		self.shortname=data[5]
		self.pan=data[6]
		self.bic=data[7].decode('ascii')

