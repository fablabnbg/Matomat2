import os
import socket
import struct
import base64
from datetime import timedelta

def tokenize_ssh_data(resp):
	pos=0
	res=[]
	while pos<len(resp):
		tl=struct.unpack_from('>I',resp,pos)[0]
		pos+=4
		res.append(resp[pos:pos+tl])
		pos+=tl
	return res

		
def create_token(time,duration=5,agent=None):
	t=time+timedelta(minutes=duration)
	if agent is None:
		agent=SSHagent()
	ts=t.isoformat()
	raw_sig=tokenize_ssh_data(agent.sign(ts.encode('ascii')))[1]
	sig=base64.standard_b64encode(raw_sig).decode('ascii')
	token=ts+'$'+sig
	return token

def get_first_id(agent=None):
	if agent is None:
		agent=SSHagent()
	ids=agent.identities()
	if not ids:
		return None
	key,comment=ids[0]
	b64key=base64.standard_b64encode(key)
	return b' '.join([b'ssh-rsa',b64key,comment]).decode('ascii')

class SSHagent:
	SSH2_AGENTC_REQUEST_IDENTITIES=11
	SSH2_AGENT_IDENTITIES_ANSWER=12
	SSH2_AGENTC_SIGN_REQUEST=13
	SSH2_AGENT_SIGN_RESPONSE=14
	def __init__(self,sock_path=None):
		if sock_path is None:
			sock_path=os.getenv('SSH_AUTH_SOCK')
		self.s=socket.socket(socket.AF_UNIX)
		self.s.connect(sock_path)
	
	def close(self):
		self.s.close()

	def _send(self,msg):
		self.s.sendall(struct.pack('>I',len(msg)))
		self.s.sendall(msg)
		return self._recv()

	def _recv(self):
		length=struct.unpack('>I',self.s.recv(4))[0]
		data=self.s.recv(length)
		return data

	def identities(self):
		resp=self._send(bytes([self.SSH2_AGENTC_REQUEST_IDENTITIES]))
		if resp[0]!=self.SSH2_AGENT_IDENTITIES_ANSWER:
			raise RuntimeError('Invalid respose to identities query. Exspected 0x0c as first byte. Got: ',resp)
		num_keys=struct.unpack('>I',resp[1:5])[0]
		res=[]
		pos=5
		for key_index in range(num_keys):
			blob_len=struct.unpack_from('>I',resp,pos)[0]
			pos+=4
			blob=resp[pos:pos+blob_len]
			pos+=blob_len
			comment_len=struct.unpack_from('>I',resp,pos)[0]
			pos+=4
			comment=resp[pos:pos+comment_len]
			pos+=comment_len
			res.append((blob,comment))
		return res

	def sign(self,data,blob=None):
		if blob is None:
			blob=self.identities()[0][0]
		cmd=struct.pack('>BI',self.SSH2_AGENTC_SIGN_REQUEST,len(blob))
		cmd+=blob
		cmd+=struct.pack('>I',len(data))
		cmd+=data
		cmd+=struct.pack('>I',0)
		resp=self._send(cmd)
		if resp[0]!=self.SSH2_AGENT_SIGN_RESPONSE:
			raise RuntimeError('Invalid respose to sign query. Exspected 0x0e as first byte. Got: ',resp)
		blob_len=struct.unpack_from('>I',resp,1)[0]
		blob=resp[5:5+blob_len]
		return blob

