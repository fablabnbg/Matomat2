#!/usr/bin/env python3
import ssh_token
import matomat_client
import tkinter as tk
from decimal import Decimal
import config
import dateutil.parser

class Connect_gui(tk.Frame):
	def __init__(self,*args,default_addr=None,cert=None,command=None,**kwargs):
		super().__init__(*args,**kwargs)
		self.addr=tk.StringVar(self,default_addr)
		tk.Entry(self,textvariable=self.addr).pack(side=tk.LEFT)
		tk.Button(self,command=self.connect,text='Connect').pack(side=tk.LEFT)
		self.connection=None
		self.cert=cert
		self.command=command

	def connect(self):
		addr=self.addr.get()
		if not addr[-1]=='/':
			addr+='/'
		m=matomat_client.Matomat_client(addr,cert=self.cert)
		try:
			m.get_date()
			self.connection=m
		except Exception as e:
			print(e)
			return
		if self.command:
			self.command(self.connection)

class Login_gui(tk.Frame):
	def __init__(self,*args,connection,command=None,**kwargs):
		super().__init__(*args,**kwargs)
		self.connection=connection
		tk.Label(self,text='Username').grid(row=0,column=0)
		tk.Label(self,text='Password').grid(row=0,column=0)
		username=self.connection.lookup(ssh_token.get_first_id())
		self.username=tk.StringVar(self,username[0])
		self.password=tk.StringVar(self)
		tk.Entry(self,textvariable=self.username).grid(row=1,column=0)
		tk.Entry(self,textvariable=self.password,show='*').grid(row=1,column=1)
		tk.Button(self,command=self.login,text='Login').grid(row=2,column=0)
		tk.Button(self,command=self.ssh,text='SSH').grid(row=2,column=1)
		self.using_ssh=False
		self.command=command

	def _login(self,username,password):
		self.connection.username=username
		self.connection.password=password
		try:
			self.connection.balance()
		except Exception as e:
			print(e)
			return
		if self.command:
			self.command(self.connection)


	def login(self):
		self._login(self.username.get(),self.password.get())

	def ssh(self):
		token=None
		try:
			token=ssh_token.create_token(self.connection.get_date())
		except Exception as e:
			print(e)
		if token:
			self._login(self.username.get(),token)

class Main_gui(tk.Frame):
	def __init__(self,*args,connection,**kwargs):
		super().__init__(*args,**kwargs)
		self.connection=connection
		self.balance=tk.StringVar(self)
		self.amount=tk.StringVar(self)
		tk.Label(self,textvariable=self.balance).pack()
		self.items=tk.Frame(self)
		self.items.pack()
		tk.Entry(self,textvariable=self.amount).pack()
		tk.Button(self,text='Deposit',command=self.pay).pack()
		tk.Button(self,text='Undo',command=self.undo).pack()
		self.refresh_items()
		self._refresh()

	def _refresh(self):
		self.refresh_balance()
		self.refresh_token()
		self.after(5000,self._refresh)

	def refresh_items(self):
		for k in self.items.children:
			self.items.children.forget()
		items=self.connection.get_items()
		for i in items:
			tk.Button(self.items,text=i['name']+' {:.3}€'.format(i['price']/100),command=lambda x=i['id']:self.buy(x)).pack()

	def refresh_balance(self):
		bal=self.connection.balance()
		self.balance.set('Balance {:.3}€'.format(bal/100))

	def refresh_token(self):
		expiry,_=self.connection.password.split('$',1)
		expiry=dateutil.parser.parse(expiry)
		date=self.connection.get_date()
		self.time_left=expiry-date
		if self.time_left.seconds>60:
			return
		token=None
		try:
			token=ssh_token.create_token(date)
		except Exception as e:
			print(e)
			return
		if token:
			self.password=token

	def buy(self,item):
		self.connection.buy(item)
		self.refresh_balance()

	def pay(self):
		try:
			amount=Decimal(self.amount.get())
		except InvalidOperation:
			print('Error: Not a number')
			return
		amount=int(100*amount)
		status,_=self.connection.pay(amount)
		if status==201:
			self.amount.set('')
		self.refresh_balance()

	def undo(self):
		self.connection.undo()
		self.refresh_balance()

		
class Matomat_gui(tk.Frame):
	def __init__(self,*args,local_config=None,**kwargs):
		super().__init__(*args,**kwargs)
		if not local_config:
			local_config=config
		self.config=local_config
		self.conn_gui=Connect_gui(self,default_addr=self.config.server,cert=self.config.cert,command=self.on_connect)
		self.conn_gui.pack()
		if self.config.autoconnect:
			self.conn_gui.connect()

	def on_connect(self,connection):
		self.conn_gui.forget()
		self.login_gui=Login_gui(self,connection=connection,command=self.on_login)
		self.login_gui.pack()
		if self.config.autossh:
			self.login_gui.ssh()

	def on_login(self,connection):
		self.login_gui.forget()
		self.main_gui=Main_gui(self,connection=connection)
		self.main_gui.pack()
	
if __name__=='__main__':
	root=tk.Tk()
	g=Matomat_gui(root)
	g.pack()
	tk.mainloop()
