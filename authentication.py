import random
import hashlib
from database import User
from sqlalchemy import func
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from datetime import datetime
import dateutil.parser
import base64
import bcrypt

def hashpw(salt,password,version):
	if version==1:
		salt,dummy=salt.split('$')
		h=hashlib.sha1()
		h.update(salt.encode('UTF-8'))
		h.update(password.encode('UTF-8'))
		return salt+'$'+h.hexdigest()
	if version==2:
		pass
	raise ValueError('Unknown Hash Version "{}"'.format(version))
	return b''

def get_user(Session,username):
	user=Session.query(User).filter(func.lower(User.name)==func.lower(username)).all()
	if len(user)!=1:
		return None
	return user[0]

def auth_ssh(Session,user,password):
	expiry_date,signature=password.split('$',1)
	expiry_date_dt=dateutil.parser.parse(expiry_date)
	if datetime.now()>expiry_date_dt:
		return None
	signature=base64.standard_b64decode(signature.encode('ascii'))
	expiry_hash=SHA.new(expiry_date.encode('ascii'))
	key=user.public_key
	if not key:
		return None
	try:
		key=RSA.importKey(key)
	except ValueError:
		return None
	pkcs=PKCS1_v1_5.new(key)

	if pkcs.verify(expiry_hash,signature):
		return user
	return None

def check_user(Session,username,password):
	if password is None:
		return None
	user=get_user(Session,username)
	if user is None:
		return None
	if len(password)>100: #assume ssh authentication if password is very long
		return auth_ssh(Session,user,password)
	version,passhash=user.password.split('$',1)
	try:
		version=int(version)
	except ValueError:
		salt=version
		passhash=salt+'$'+passhash
		version=1
	if passhash==hashpw(passhash,password,version):
		return user
	return None

def genpw(password):
	saltbase=(
		[chr(x) for x in range(ord('A'),ord('Z')+1)]+
		[chr(x) for x in range(ord('a'),ord('z')+1)]+
		[chr(x) for x in range(ord('0'),ord('9')+1)]
		)
	salt=''.join(random.sample(saltbase,10))
	version=1
	return '$'.join([str(version),hashpw(salt+'$',password,version)])

def create_user(Session,username,password,public_key,creator):
	s=Session
	user=get_user(s,username)
	if user is None:
		if creator:
			cid=creator.id
		else:
			cid=None
		u=User(name=username,password=genpw(password),creator=cid,public_key=public_key)
		s.add(u)
		s.commit()
		return True
	else:
		u=user
		if not creator: return False
		if u.id==creator.id or creator.name=='admin':
			if not password is None:
				if password=='':
					u.password=''
				else:
					u.password=genpw(password)
			if not public_key is None:
				u.public_key=public_key
			s.merge(u)
			s.commit()
			return True
	return False

