from datetime import datetime
from sqlalchemy import DateTime, cast
import database as db

def collate_by_user(data):
	res=dict()
	for d in data:
		try:
			oldval=res[d.user]
		except KeyError:
			oldval=0
		res[d.user]=oldval+d.amount
	return res

def discard_overdrawn(data):
	good=dict()
	bad=dict()
	for d in data:
		if d.max_sepa_amount>=data[d]:
			good[d]=data[d]
		else:
			bad[d]=data[d]
	return (good,bad)

def create_debit_file(data):
	by_user=collate_by_user(data)
	return discard_overdrawn(by_user)

