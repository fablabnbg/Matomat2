from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine

Base=declarative_base()

class User(Base):
	__tablename__='users'
	id=Column(Integer,primary_key=True)
	name=Column(String(32),unique=True)
	password=Column(String(128))
	creator=Column(Integer,nullable=True)
	iban=Column(String(34),nullable=True)
	max_sepa_amount=Column(Integer, default=5000)
	right_accountant=Column(Boolean, default=False)

class Item(Base):
	__tablename__='items'
	id=Column(Integer,primary_key=True)
	name=Column(String(32))
	price=Column(Integer)

class Sale(Base):
	__tablename__='sales'
	id=Column(Integer,primary_key=True)
	user_id=Column(Integer,ForeignKey('users.id'))
	item_id=Column(Integer,ForeignKey('items.id'))
	amount=Column(Integer)
	time=Column(DateTime, default=func.now())
	user=relationship('User')
	item=relationship('Item')

class Pay(Base):
	__tablename__='pays'
	id=Column(Integer,primary_key=True)
	user_id=Column(Integer,ForeignKey('users.id'))
	amount=Column(Integer)
	time=Column(DateTime, default=func.now())
	user=relationship('User')

class PaySepa(Base):
	__tablename__='payssepa'
	id=Column(Integer,primary_key=True)
	user_id=Column(Integer,ForeignKey('users.id'))
	amount=Column(Integer)
	time=Column(DateTime, default=func.now())
	user=relationship('User')

class Transfer(Base):
	__tablename__='transfers'
	id=Column(Integer,primary_key=True)
	sender_id=Column(Integer,ForeignKey('users.id'))
	recipient_id=Column(Integer,ForeignKey('users.id'))
	amount=Column(Integer)
	time=Column(DateTime, default=func.now())
	sender=relationship('User', foreign_keys=sender_id)
	recipient=relationship('User',foreign_keys=recipient_id)

def create_sessionmaker(dbengine):
	__engine=create_engine(dbengine)
	Base.metadata.create_all(__engine)
	Session=sessionmaker(bind=__engine)
	return Session
