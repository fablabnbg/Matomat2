from authentication import check_user, create_user, get_user
from datetime import datetime
from functools import reduce
from sqlalchemy.sql import func
import database as db
import config

class NotAuthenticatedError(Exception):
	pass

class matomat_factory(object):
	def __init__(self,engine):
		self.Session=db.create_sessionmaker(engine)

	def get(self):
		return matomat(self.Session())

def require_auth(fun):
	def inner(self,*args,**kwargs):
		if not self.is_auth():
			raise NotAuthenticatedError('Not authenticated')
		return fun(self,*args,**kwargs)
	return inner

def require_admin(fun):
	fun=require_auth(fun)
	def inner(self,*args,**kwargs):
		if not self._user.name=="admin":
			raise NotAuthenticatedError('Not admin')
		return fun(self,*args,**kwargs)
	return inner



class matomat(object):
	def __init__(self, dbsession):
		self._user=None
		self.session=dbsession

	def close(self):
		self.session.close()

	def is_auth(self):
		return not self._user is None

	def auth(self,user,password):
		user=check_user(self.session,user,password)
		if user is None:
			return False
		self._user=user
		return True

	def total_balance(self):
		money_in=int(self.session.query(func.sum(db.Pay.amount)).scalar() or 0)
		money_out=int(self.session.query(func.sum(db.Sale.amount)).scalar() or 0)
		external_in=int(self.session.query(func.sum(db.PayExternal)).scalar() or 0)
		res=money_in-money_out+external_in
		return res

	@require_auth
	def balance(self):
		#empty tables return None instead of 0. So replace Nones with 0s
		money_in=int(self.session.query(func.sum(db.Pay.amount)).filter(db.Pay.user==self._user).scalar() or 0)
		money_out=int(self.session.query(func.sum(db.Sale.amount)).filter(db.Sale.user==self._user).scalar() or 0)
		transfers_in=int(self.session.query(func.sum(db.Transfer.amount)).filter(db.Transfer.recipient==self._user).scalar() or 0)
		transfers_out=int(self.session.query(func.sum(db.Transfer.amount)).filter(db.Transfer.sender==self._user).scalar() or 0)
		external_in=int(self.session.query(func.sum(db.PayExternal.amount)).filter(db.PayExternal.user==self._user).scalar() or 0)
		res=money_in-money_out+transfers_in-transfers_out+external_in
		return res

	@require_auth
	def details(self):
		money_in=self.session.query(db.Pay).filter(db.Pay.user==self._user).all()
		money_out=self.session.query(db.Sale).filter(db.Sale.user==self._user).all()
		transfers_in=self.session.query(db.Transfer).filter(db.Transfer.recipient==self._user).all()
		transfers_out=self.session.query(db.Transfer).filter(db.Transfer.sender==self._user).all()
		external_in=self.session.query(db.PayExternal).filter(db.PayExternal.user==self._user).all()

		money=sorted(money_in+money_out+transfers_in+transfers_out+external_in,key=lambda x:x.time,reverse=True)
		data=[]
		for m in money:
			d={"amount":m.amount,"time":m.time.isoformat()}
			if isinstance(m,db.Sale):
				d["amount"]*=-1
				if m.item is not None:
					d["Item"]=m.item.name
				else:
					d["Item"]='<<<Deleted Item>>>'
			if isinstance(m,db.Transfer):
				if m.sender==self._user:
					d["amount"]*=-1
				d["sender"]=m.sender.name
				d["recipient"]=m.recipient.name
			data.append(d)
		return data

	@require_auth
	def username(self):
		return self._user.name

	@require_auth
	def create_user(self,username,password,public_key):
		if not create_user(self.session,username,password,public_key,self._user):
			raise ValueError("Cannot change different user's password")

	@require_auth
	def pay(self,amount):
		p=db.Pay(user=self._user,amount=int(amount))
		self.session.add(p)
		self.session.commit()
		for plugin in config.plugins:
			plugin.pay(self)

	@require_auth
	def payexternal(self,amount):
		if self._user.external_id is None:
			raise EnvironmentError('No payment processor id available for user {}')
		if not config.payment_processor.debit(self._user.external_id,amount,'Matomat'):
			raise EnvironmentError('Payment failed')
		p=db.PayExternal(user=self._user,amount=int(amount))
		self.session.add(p)
		self.session.commit()
		for plugin in config.plugins:
			plugin.pay(self)
	
	@require_auth
	def buy(self,item):
		if isinstance(item,int):
			item=self.lookup_item(item)
		sale=db.Sale(user=self._user,item=item,amount=item.price)
		self.session.add(sale)
		self.session.commit()
		for plugin in config.plugins:
			plugin.sale(self)

	@require_auth
	def transfer(self,amount,to):
		if not isinstance(to,db.User):
			to=get_user(self.session,to)
			if to is None:
				raise ValueError('Unknown User')
		amount=int(amount)
		if amount<0:
			raise ValueError('Can only transfer positive amounts')
		transfer=db.Transfer(sender=self._user,recipient=to,amount=amount)
		self.session.add(transfer)
		self.session.commit()

	@require_auth
	def undo(self):
		last_in=self.session.query(db.Pay).filter(db.Pay.user==self._user).order_by(db.Pay.time.desc()).first()
		last_out=self.session.query(db.Sale).filter(db.Sale.user==self._user).order_by(db.Sale.time.desc()).first()
		candidates=[]
		if not last_in is None: candidates.append(last_in)
		if not last_out is None: candidates.append(last_out)
		if len(candidates)==0: return
		to_del=max(candidates,key=lambda x:x.time)
		self.session.delete(to_del)
		self.session.commit()
		for plugin in config.plugins:
			plugin.undo(self)

	@require_admin
	def add_item(self,name,price,id=None):
		i=db.Item(id=id,name=name,price=price)
		self.session.merge(i)
		self.session.commit()

	@require_admin
	def delete_item(self,item):
		if isinstance(item,int):
			item=self.lookup_item(item)
		self.session.delete(item)
		self.session.commit()

	def lookup_item(self,item_id):
		item=self.session.query(db.Item).filter(db.Item.id==item_id).one()
		return item

	def lookup_user(self,user_id):
		if type(user_id)==str:
			user_id=user_id.rstrip()
			return reduce(lambda x,y:x+y,self.session.query(db.User).filter(db.User.public_key==user_id).values('name'))
			return [x.name for x in self.session.query(db.User).filter(db.User.public_key==user_id).all()]
		user=self.session.query(db.User).filter(db.User.id==user_id).one()
		return user

	def items(self):
		items_q=self.session.query(db.Item)
		items=[{"id":x.id,"name":x.name,"price":x.price} for x in items_q]
		return items

