from authentication import check_user, create_user, get_user
from datetime import datetime
import sepa
import database as db

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


class matomat(object):
	def __init__(self, dbsession):
		self._user=None
		self.session=dbsession

	def is_auth(self):
		return not self._user is None

	def auth(self,user,password):
		user=check_user(self.session,user,password)
		if user is None:
			return False
		self._user=user
		return True

	@require_auth
	def balance(self):
		money_in=sum((x.amount for x in self.session.query(db.Pay).filter(db.Pay.user==self._user)))
		money_out=sum((x.amount for x in self.session.query(db.Sale).filter(db.Sale.user==self._user)))
		transfers_in=sum((x.amount for x in self.session.query(db.Transfer).filter(db.Transfer.recipient==self._user)))
		transfers_out=sum((x.amount for x in self.session.query(db.Transfer).filter(db.Transfer.sender==self._user)))
		sepa_in=sum((x.amount for x in self.session.query(db.PaySepa).filter(db.PaySepa.user==self._user)))
		res=money_in-money_out+transfers_in-transfers_out+sepa_in
		return res

	@require_auth
	def details(self):
		money_in=self.session.query(db.Pay).filter(db.Pay.user==self._user).all()
		money_out=self.session.query(db.Sale).filter(db.Sale.user==self._user).all()
		transfers_in=self.session.query(db.Transfer).filter(db.Transfer.recipient==self._user).all()
		transfers_out=self.session.query(db.Transfer).filter(db.Transfer.sender==self._user).all()
		sepa_in=self.session.query(db.PaySepa).filter(db.PaySepa.user==self._user).all()
		for m in transfers_out:
			m.amount*=-1
		money=sorted(money_in+money_out+transfers_in+transfers_out+sepa_in,key=lambda x:x.time,reverse=True)
		data=[]
		for m in money:
			d={"amount":m.amount,"time":m.time.isoformat()}
			if isinstance(m,db.Sale):
				d["amount"]*=-1
				d["Item"]=m.item.name
			if isinstance(m,db.Transfer):
				d["sender"]=m.sender.name
				d["recipient"]=m.recipient.name
			data.append(d)
		return data

	@require_auth
	def username(self):
		return self._user.name

	@require_auth
	def create_user(self,username,password):
		if not create_user(self.session,username,password,self._user):
			raise ValueError("Cannot change different user's password")

	@require_auth
	def pay(self,amount):
		p=db.Pay(user=self._user,amount=int(amount))
		self.session.add(p)
		self.session.commit()

	@require_auth
	def get_sepa_file(self,year,month):
		if not self._user.right_accountant:
			raise NotAuthenticatedError('Need Accountant right')
		time0=datetime(year,month,1)
		month+=1
		if month>12:
			month-=12
			year+=1
		time1=datetime(year,month,1)
		data=self.session.query(db.PaySepa).filter(db.PaySepa.time>=time0, db.PaySepa.time<time1).all()
		return sepa.create_debit_file(data)
	
	@require_auth
	def paysepa(self,amount):
		if self._user.iban is None:
			raise EnvironmentError('No IBAN available for user {}')
		p=db.PaySepa(user=self._user,amount=int(amount))
		self.session.add(p)
		self.session.commit()
	
	@require_auth
	def buy(self,item):
		if isinstance(item,int):
			item=self.lookup_item(item)
		sale=db.Sale(user=self._user,item=item,amount=item.price)
		self.session.add(sale)
		self.session.commit()

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
		last_transfer=self.session.query(db.Transfer).filter(db.Transfer.sender==self._user).order_by(db.Transfer.time.desc()).first()
		candidates=[]
		if not last_in is None: candidates.append(last_in)
		if not last_out is None: candidates.append(last_out)
		if not last_transfer is None: candidates.append(last_transfer)
		if len(candidates)==0: return
		to_del=max(candidates,key=lambda x:x.time)
		self.session.delete(to_del)
		self.session.commit()

	@require_auth
	def add_item(self,name,price,id=None):
		i=db.Item(id=id,name=name,price=price)
		self.session.merge(i)
		self.session.commit()

	@require_auth
	def delete_item(self,item):
		if isinstance(item,int):
			item=self.lookup_item(item)
		self.session.delete(item)
		self.session.commit()

	def lookup_item(self,item_id):
		item=self.session.query(db.Item).filter(db.Item.id==item_id).one()
		return item

	def lookup_user(self,user_id):
		user=self.session.query(db.User).filter(db.User.id==user_id).one()
		return user

	def items(self):
		items_q=self.session.query(db.Item)
		items=[{"id":x.id,"name":x.name,"price":x.price} for x in items_q]
		return items

