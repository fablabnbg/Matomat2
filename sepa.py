from datetime import datetime
from sqlalchemy import DateTime, cast
import database as db

def collate_by_iban(data):
	res=dict()
	for d in data:
		try:
			oldval=res[d.user.iban]
		except KeyError:
			oldval=0
		res[d.user.iban]=oldval+d.amount
	return res

def create_debit_file(data):
	return collate_by_iban(data)

