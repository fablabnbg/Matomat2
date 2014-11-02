import random
import hashlib
from database import User
from sqlalchemy import func

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

def check_user(Session,username,password):
	if password is None:
		return None
	user=get_user(Session,username)
	if user is None:
		return None
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

def create_user(Session,username,password,creator):
	s=Session
	user=get_user(s,username)
	if user is None:
		u=User(name=username,password=genpw(password),creator=creator.id)
		s.add(u)
		s.commit()
		return True
	else:
		u=user
		if u.id==creator.id or creator.name=='admin':
			u.password=genpw(password)
			s.merge(u)
			s.commit()
			return True
	return False

