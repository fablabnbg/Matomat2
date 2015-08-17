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

def hashpw(salt,password):
	h=hashlib.sha1()
	h.update(salt)
	h.update(password)
	return h.hexdigest()

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
	salt_hashed=user.password.split('$',1)
	if len(salt_hashed)!=2:
		return None
	salt,hashed=salt_hashed
	if hashed==hashpw(salt.encode('ASCII'),password.encode('UTF-8')):
		return user
	return None

def genpw(password):
	saltbase=(
		[bytes([x]) for x in range(ord('A'),ord('Z')+1)]+
		[bytes([x]) for x in range(ord('a'),ord('z')+1)]+
		[bytes([x]) for x in range(ord('0'),ord('9')+1)]
		)
	salt=b''.join(random.sample(saltbase,10))
	return ''.join([salt.decode('ASCII'),'$',hashpw(salt,password.encode('UTF-8'))])

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
		if u.id==creator.id or creator.name=='admin':
			u.password=genpw(password)
			u.public_key=public_key
			s.merge(u)
			s.commit()
			return True
	return False

