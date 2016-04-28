#!/usr/bin/env python3

import unittest

import authentication as auth
import database as db

class test_auth(unittest.TestCase):
	def setUp(self):
		self.s=db.create_sessionmaker('sqlite://')()
		u=db.User(name='test',password='PUQNajhroe$6068b411a6f27821dc9473b8a26b7813b22ebcd7') # password is 'pass'
		self.s.add(u)
		u=db.User(name='test_1',password='PUQNajhroe$6068b411a6f27821dc9473b8a26b7813b22ebcd7') # password is 'pass'
		self.s.add(u)
		u=db.User(name='test_2',password='PUQNajhroe$6068b411a6f27821dc9473b8a26b7813b22ebcd7') # password is 'pass'
		self.s.add(u)
		u=db.User(name='admin',password='PUQNajhroe$6068b411a6f27821dc9473b8a26b7813b22ebcd7') # password is 'pass'
		self.s.add(u)
		self.s.commit()

	def test_get_user_existing(self):
		u=auth.get_user(self.s,'test')
		self.assertEqual(u.name,'test')

	def test_get_user_not_existing(self):
		u=auth.get_user(self.s,'invalid')
		self.assertIsNone(u)

	def test_check_user_fail(self):
		u=auth.check_user(self.s,'test','test1')
		self.assertIsNone(u)

	def test_check_user_success(self):
		u=auth.check_user(self.s,'test','pass')
		self.assertEqual(u.name,'test')
		self.assertNotEqual(u.password,'PUQNajhroe$6068b411a6f27821dc9473b8a26b7813b22ebcd7')

	def test_create_user_new_no_creator(self):
		self.assertTrue(auth.create_user(self.s,'test_new','pass',None,None))
		u=auth.get_user(self.s,'test_new')
		self.assertEqual(u.name,'test_new')

	def test_create_user_new_creator(self):
		u=auth.get_user(self.s,'test')
		self.assertTrue(auth.create_user(self.s,'test_new','pass',None,u))
		u=auth.get_user(self.s,'test_new')
		self.assertEqual(u.name,'test_new')

	def test_create_user_update_no_creator(self):
		self.assertFalse(auth.create_user(self.s,'test','pass2',None,None))
		u=auth.check_user(self.s,'test','pass')
		self.assertIsNotNone(u)

	def test_create_user_update_self(self):
		u=auth.get_user(self.s,'test')
		self.assertTrue(auth.create_user(self.s,'test','pass2',None,u))
		u=auth.check_user(self.s,'test','pass2')
		self.assertIsNotNone(u)

	def test_create_user_update_other(self):
		u=auth.get_user(self.s,'test_1')
		self.assertFalse(auth.create_user(self.s,'test','pass2',None,u))
		u=auth.check_user(self.s,'test','pass')
		self.assertIsNotNone(u)

	def test_create_user_update_admin(self):
		u=auth.get_user(self.s,'admin')
		self.assertTrue(auth.create_user(self.s,'test','pass2',None,u))
		u=auth.check_user(self.s,'test','pass2')
		self.assertIsNotNone(u)

if __name__=='__main__':
	unittest.main()
