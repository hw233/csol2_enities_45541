# -*- coding: utf_8 -*-
import sys, socket, select, string
from time import sleep
import struct, os, time, re
import random, threading

__all__ = ["Telnet"]
TELNET_PORT = 23

# Telnet protocol characters (don't change)
IAC  = chr(255) # "Interpret As Command"
DONT = chr(254)
DO   = chr(253)
WONT = chr(252)
WILL = chr(251)
theNULL = chr(0)

class Telnet:
	def __init__(self, nHost=None, nPort=0):
		self.nHost = nHost
		self.nPort = nPort
		self.sock = None
		self.rawq = ''
		self.irawq = 0
		self.cookedq = ''
		self.eof = 0
		if nHost:
			self.open(nHost, nPort)

	def open(self, nHost, nPort=0):
		self.eof = 0
		if not nPort:
			nPort = TELNET_PORT
		self.nHost = nHost
		self.nPort = nPort
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.nHost, self.nPort))

	def __del__(self):
		self.close()

	def close(self):
		if self.sock:
			self.sock.close()
		self.sock = 0
		self.eof = 1

	def fileno(self):
		return self.sock.fileno()

	def write(self, buffer):
		if IAC in buffer:
			buffer = buffer.replace(IAC, IAC+IAC)
		self.sock.send(buffer)

	def read_until(self, match, timeout=None):
		nSize = len(match)
		self.process_rawq()
		nIndex = self.cookedq.find(match)
		if nIndex >= 0:
			nIndex = nIndex + nSize
			buf = self.cookedq[:nIndex]
			self.cookedq = self.cookedq[nIndex:]
			return buf
		s_reply = ([self], [], [])
		s_args = s_reply
		if timeout is not None:
			s_args = s_args + (timeout,)
		while not self.eof and apply(select.select, s_args) == s_reply:
			nIndex = max(0, len(self.cookedq) - nSize)
			self.fill_rawq()
			self.process_rawq()
			nIndex = self.cookedq.find(match, nIndex)
			if nIndex >= 0:
				nIndex = nIndex + nSize
				buf = self.cookedq[:nIndex]
				self.cookedq = self.cookedq[nIndex:]
				return buf
		return self.read_result()

	def read_result(self):
		buf = self.cookedq
		self.cookedq = ''
		if not buf and self.eof and not self.rawq:
			raise EOFError, 'telnet connection closed'
		return buf

	def read_current(self):
		self.process_rawq()
		while not self.cookedq and not self.eof:
			self.fill_rawq()
			self.process_rawq()
		buf = self.cookedq
		self.cookedq = ''
		return buf

	def process_rawq(self):
		buf = ''
		try:
			while self.rawq:
				c = self.rawq_getchar()
				if c == theNULL:
					continue
				if c == "\021":
					continue
				if c != IAC:
					buf = buf + c
					continue
				c = self.rawq_getchar()
				if c == IAC:
					buf = buf + c
				elif c in (DO, DONT):
					opt = self.rawq_getchar()
					self.sock.send(IAC + WONT + opt)
				elif c in (WILL, WONT):
					opt = self.rawq_getchar()
					self.sock.send(IAC + DONT + opt)
				else:
					pass
		except EOFError: # raised by self.rawq_getchar()
			pass
		self.cookedq = self.cookedq + buf

	def rawq_getchar(self):
		if not self.rawq:
			self.fill_rawq()
			if self.eof:
				raise EOFError
		c = self.rawq[self.irawq]
		self.irawq = self.irawq + 1
		if self.irawq >= len(self.rawq):
			self.rawq = ''
			self.irawq = 0
		return c

	def fill_rawq(self):
		if self.irawq >= len(self.rawq):
			self.rawq = ''
			self.irawq = 0
		buf = self.sock.recv(50)
		self.eof = (not buf)
		self.rawq = self.rawq + buf

	def sock_avail(self):
		return select.select([self], [], [], 0) == ([self], [], [])

	def expect(self, list, timeout=None):
		re = None
		list = list[:]
		indices = range(len(list))
		for nIndex in indices:
			if not hasattr(list[i], "search"):
				if not re: import re
				list[nIndex] = re.compile(list[nIndex])
		while 1:
			self.process_rawq()
			for nIndex in indices:
				nNum = list[i].search(self.cookedq)
				if nNum:
					e = nNum.end()
					text = self.cookedq[:e]
					self.cookedq = self.cookedq[e:]
					return (nIndex, nNum, text)
			if self.eof:
				break
			if timeout is not None:
				r, w, x = select.select([self.fileno()], [], [], timeout)
				if not r:
					break
			self.fill_rawq()
		text = self.read_result()
		if not text and self.eof:
			raise EOFError
		return (-1, None, text)

def telnetCellApp():
	while sys.argv[1:] and sys.argv[1] == '-d':
		del sys.argv[1]
	nHost = '172.16.0.244'
	if sys.argv[1:]:
		nHost = sys.argv[1]
	nPort = 40001
	if sys.argv[2:]:
		portstr = sys.argv[2]
		try:
			nPort = int(portstr)
		except ValueError:
			nPort = socket.getservbyname(portstr, 'tcp')
	tn = Telnet()
	tn.open(nHost, nPort)
	print tn.read_until('>>>', 2)
	nLoop = 0
	nTotal = 0
	while True:
		tn.write('len(BigWorld.entities.values())\r\n')
		strRet = tn.read_until('>>>', 3)
		# print strRet
		if strRet:
			strList = strRet.split('\n')
			nNumber = string. atoi(strList[1])
			if nLoop == 0:
				nTotal = nNumber
			nBots = (nNumber - nTotal) / 2
			print "Total Added players is: %d" % nBots
		nLoop += 1
		sleep(3)
	tn.close()

def stataRoleNumber3():
		while sys.argv[1:] and sys.argv[1] == '-d':
			del sys.argv[1]
		nHost = '172.16.0.242'
		nHost1 = '172.16.0.243'
		nHost2 = '172.16.0.244'
		if sys.argv[1:]:
				nHost = sys.argv[1]
		nPort = 40001
		if sys.argv[2:]:
				portstr = sys.argv[2]
				try:
						nPort = int(portstr)
				except ValueError:
						nPort = socket.getservbyname(portstr, 'tcp')
		tn = Telnet()
		tn1 = Telnet()
		tn2 = Telnet()
		tn.open(nHost, nPort)
		tn1.open(nHost1, nPort)
		tn2.open(nHost2, nPort)
		print tn.read_until('>>>', 3)
		print tn1.read_until('>>>', 3)
		print tn2.read_until('>>>', 3)
		nNum = 0
		nNum1 = 0
		nNum2 = 0
		while True:
			tn.write("len([i for i in BigWorld.entities.values() if i.__class__.__name__=='Role'])\r\n")
			strTmp = tn.read_until('>>>', 3)
			strList = strTmp.split('\n')
			if strList[1]:
				nNum = string.atoi(strList[1])
			tn1.write("len([i for i in BigWorld.entities.values() if i.__class__.__name__=='Role'])\r\n")
			strTmp = tn1.read_until('>>>', 3)
			strList = strTmp.split('\n')
			if strList[1]:
				nNum1 = string.atoi(strList[1])
			tn2.write("len([i for i in BigWorld.entities.values() if i.__class__.__name__=='Role'])\r\n")
			strTmp = tn2.read_until('>>>', 3)
			strList = strTmp.split('\n')
			if strList[1]:
				nNum1 = string.atoi(strList[1])
			sleep(3)
			print "%s have role NUMBER is = %d" % (nHost, nNum)
			print "%s have role NUMBER is = %d" % (nHost1, nNum1)
			print "%s have role NUMBER is = %d" % (nHost2, nNum2)
			print "total NUMBER is = %d" % (nNum + nNum1 + nNum2)
		tn.close()
		tn1.close()
		tn2.close()

def stataRoleNumber2():
		while sys.argv[1:] and sys.argv[1] == '-d':
			del sys.argv[1]
		nHost = '172.16.0.242'
		nHost1 = '172.16.0.243'
		if sys.argv[1:]:
				nHost = sys.argv[1]
		nPort = 40001
		if sys.argv[2:]:
				portstr = sys.argv[2]
				try:
						nPort = int(portstr)
				except ValueError:
						nPort = socket.getservbyname(portstr, 'tcp')
		tn = Telnet()
		tn1 = Telnet()
		tn.open(nHost, nPort)
		tn1.open(nHost1, nPort)
		print tn.read_until('>>>', 3)
		print tn1.read_until('>>>', 3)
		nNum = 0
		nNum1 = 0
		while True:
			tn.write("len([i for i in BigWorld.entities.values() if i.__class__.__name__=='Role'])\r\n")
			strTmp = tn.read_until('>>>', 3)
			strList = strTmp.split('\n')
			if strList[1]:
				nNum = string.atoi(strList[1])
			tn1.write("len([i for i in BigWorld.entities.values() if i.__class__.__name__=='Role'])\r\n")
			strTmp = tn1.read_until('>>>', 3)
			strList = strTmp.split('\n')
			if strList[1]:
				nNum1 = string.atoi(strList[1])
			sleep(3)
			print "%s have role NUMBER is = %d" % (nHost, nNum)
			print "%s have role NUMBER is = %d" % (nHost1, nNum1)
			print "total NUMBER is = %d" % (nNum + nNum1)
		tn.close()
		tn1.close()

def stataRoleNumber():
	while sys.argv[1:] and sys.argv[1] == '-d':
		del sys.argv[1]
	nHost = '172.16.0.244'
	if sys.argv[1:]:
		nHost = sys.argv[1]
	nPort = 40001
	if sys.argv[2:]:
		portstr = sys.argv[2]
		try:
			nPort = int(portstr)
		except ValueError:
			nPort = socket.getservbyname(portstr, 'tcp')
	tn = Telnet()
	tn.open(nHost, nPort)
	print tn.read_until('>>>', 3)
	while True:
		tn.write("len([i for i in BigWorld.entities.values() if i.__class__.__name__=='Role'])\r\n")
		strTmp = tn.read_until('>>>', 3)
		strList = strTmp.split('\n')
		if strList[1]:
			print strList[1]
		sleep(1)
	tn.close()
	"""
	amount = 0
	for i in BigWorld.entities.values():
		if i.__class__.__name__ == 'Role':
		    amount += 1
	return amount
	"""

def telnetBots():
	# strHost = '172.16.0.242'
	print "请输Bots的IP最后三位数字！"
	strEndIp = sys.stdin.readline()
	strHost = '172.16.0.%s' % strEndIp
	print "请输入Bots的端口号，纯数字啊!"
	nPort = string.atoi(sys.stdin.readline())
	tn = Telnet()
	tn.open(strHost, nPort)
	print tn.read_current()
	print "请输入要增加的Bots的数量!"
	nNumber = string.atoi(sys.stdin.readline())
	tn.write('BigWorld.addBotsSlowly(%d, 5)\r\n' % nNumber)
	print tn.read_until('>>>', 3)
	sleep( nNumber * 6 )
	telnetChatBots(tn, nNumber)
	tn.close()

BOT_STATE_NULL	= 0x00									# 无	
BOT_STATE_CHAT	= 0x01									# 聊天
BOT_STATE_FIGHT = 0x02									# 战斗
BOT_STATE_EQUIP = 0x04									# 装备
BOT_STATE_ALL = BOT_STATE_EQUIP | BOT_STATE_FIGHT | BOT_STATE_CHAT
BOT_STATE_NOW = BOT_STATE_EQUIP | BOT_STATE_CHAT 
def telnetChatBots(tn, nNuber):
	strList = []
	nFlag = 0
	nCounter = 0
	while nFlag < nNuber:
		tn.write("for id,bot in BigWorld.bots.items():print id\r\n")
		strRet = tn.read_until('>>>', 3)
		strList = strRet.split("\n")
		nFlag = 0
		tn.write("roleList = []\r\n")
		for strID in strList:
			if strID.find('>>>') >= 0:
				continue
			if strID == '0\r' or strID == '\r':
				continue
			if nFlag != 0:
				nID = string.atoi(strID)
				tn.write("role = BigWorld.bots[%d].entities[%d]\r\n" % (nID, nID))
				tn.write("if role.__class__.__name__ == 'Role':roleList.append(role)\r\n")
				tn.write("if role.__class__.__name__ == 'Role':role.beginBotLoop(%d)\r\n" % BOT_STATE_NOW )
				# print nID
			nFlag += 1
		sleep(1)
		nCounter += 1
		if nCounter > 10:
			break
	print strList

def threadTelnet():
	while True:
		if os.path.exists('bots'):
			sleep(6)
			print "请输入要执行的时间，例如 13:35  注意全角字符...\n >>>"
			strTime = sys.stdin.readline()
			print " <<<"
			lstTime = strTime.split(':')
			if lstTime:
				print "正在等待处理 ... ..."
				autoAddBots(int(lstTime[1]))
			else:
				print "输入的时间格式可能不对哦 ... "
		sleep(3)

def startBotsAndTelnet():
	if os.path.exists('bots'):
		os.remove('bots')
	ReadingThread = threading.Thread(target=threadTelnet)
	ReadingThread.start()
	strCmd = '..\\..\\..\\bots.exe'
	os.system(strCmd)

time_server = ('172.16.0.254', 123)
TIME1970 = 2208988800L
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
pdata = '\x1b' + 47 * '\0'

def getServerTime():
	global pdata
	client.sendto(pdata, time_server)
	data, address = client.recvfrom(1024)
	if data:
	    # print 'Response received from', address,'\n'
	    nRet = struct.unpack( '!12I', data )[10]
	    if nRet == 0:
	        raise 'invalid response'
	    return nRet
	else:
	    raise 'no data returned'

def autoAddBots(nMinute):
	ff = open('bots', 'r')
	nPort = int(ff.read())
	ff.close()
	os.remove('bots')
	hf = os.popen('ipconfig', 'r')
	lstText = hf.read().split('\n')
	hf.close()
	rex = re.compile(r'IP Address[\. ]+:[ ]172\.16\.[0-9\.]+')
	strHost = ""
	for strLine in lstText:
		if rex.findall(strLine):
			strHost = strLine.split(':')[1].strip()
	ff = open('botsNumber', 'w')
	tn = Telnet()
	tn.open(strHost, nPort)
	tn.read_until('>>>', 10)
	nSerCount = getServerTime()
	nLocCount = int(time.time() + TIME1970 + 0.5)
	nTimeRange = nSerCount - nLocCount
	tm = time.localtime(time.time())
	nFixTime = nLocCount - tm[4] * 60 - tm[5] + nMinute * 60
	while True:
		nNowTime = int(time.time() + TIME1970 + 0.5) + nTimeRange
		if nNowTime == nFixTime:
			nIndex = 0
			while nIndex < 1:
				nBots = random.randint(0, 5) + 10
				tn.write('BigWorld.addBots(%d)\r\n' % 10)
				# tn.write('BigWorld.addBotsSlowly(%d,5)\r\n' % 100)
				tn.read_until('>>>', 3)
				ff.write('%d\n' % nBots)
				sleep(1)
				nIndex += 1
			break
	tn.close()
	ff.close()

def AddBotsSlowly():
	ff = open('bots', 'r')
	nPort = int(ff.read())
	ff.close()
	os.remove('bots')
	hf = os.popen('ipconfig', 'r')
	lstText = hf.read().split('\n')
	hf.close()
	rex = re.compile(r'IP Address[\. ]+:[ ]172\.16\.[0-9\.]+')
	strHost = ""
	for strLine in lstText:
		if rex.findall(strLine):
			strHost = strLine.split(':')[1].strip()
	tn = Telnet()
	tn.open(strHost, nPort)
	tn.read_until('>>>', 10)
	nBots = random.randint(0, 5) + 15
	tn.write('BigWorld.addBotsSlowly(%d,5)\r\n' % nBots)
	tn.read_until('>>>', 3)
	tn.close()

if __name__ == '__main__':
	# telnetCellApp()
	# telnetBots()
	# AddBotsSlowly()
	startBotsAndTelnet()
	
	
