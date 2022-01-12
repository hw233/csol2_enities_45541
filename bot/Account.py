# -*- coding: utf_8 -*-
from encodings import gb18030
import BigWorld, Math
import struct, random, re, os, string, sys
from time import sleep
from random import choice

# --------------------------------------------------------------------
# account before login, just for connection
# --------------------------------------------------------------------
class Account( BigWorld.Entity ) :
	
	ms_nIndex = 0
	def __init__(self) :
		BigWorld.Entity.__init__( self )
		self.nList = [0x0 | 0x10 | 1 << 20, 0x0 | 0x20 | 1 << 20, 0x0 | 0x30 | 1 << 20, 0x0 | 0x40 | 1 << 20 , 0x1 | 0x10 | 2 << 20, 0x1 | 0x20 | 2 << 20, 0x1 | 0x30 | 2 << 20 , 0x1 | 0x40 | 2 << 20]
		self.nIndex = random.randint(0, len(self.nList) - 1)
		strIp = ''
		if sys.platform == 'win32':
			hf = os.popen('ipconfig', 'r')
			lstText = hf.read().split('\n')
			hf.close()
			rex = re.compile(r'IP Address[\. ]+:[ ]172\.16\.[0-9\.]+')
			for strLine in lstText:
				if rex.findall(strLine):
					strIp = strLine.split('.')[-1].strip()
		else:
			import socket, fcntl
			sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			strIpList = socket.inet_ntoa(fcntl.ioctl(sk.fileno(), 0x8915, struct.pack('256s', "eth0"[:15]))[20:24]).split('.')
			if strIpList[3]:
				strIp = strIpList[3]
		ch = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
		nm = '0123456789'
		strList = [choice(ch), choice(nm), choice(ch), choice(ch), choice(nm), choice(ch), choice(ch), choice(nm)]
		strRandName = ""
		for strIndex in strList:
			strRandName += strIndex
		self.m_strRoleName = "%s%s%d" % (strIp, strRandName, self.__class__.ms_nIndex)
		self.__class__.ms_nIndex += 1
		self.m_RoleId = 0

	# ----------------------------------------------------------------
	# called by base
	# ----------------------------------------------------------------
	def initRolesCB( self, loginRoles ) :
		"""
		<defined/>
		接收到账号了所有的角色
		@type					loginRoles : list
		@param					locinRoles : 角色列表，角色详细信息，请观看：RoleMaker.RoleInfo 的初始化
		"""
		if len(loginRoles) > 0:
			self.addRoleCB(loginRoles[0])
		else:
			self.base.createRole(self.nList[self.nIndex], self.m_strRoleName, 0, 0, 0)

	def addRoleCB( self, loginRole ) :
		"""
		<defined/>
		创建一个角色的服务器返回
		@type					loginRole : dict
		@param					loginRole : 角色详细信息，请观看：RoleMaker.RoleInfo 的初始化
		"""
		self.m_RoleId = loginRole["roleID"]
		print "===================== role id FROM DATABASE is : ", loginRole["roleID"]
		if self.m_RoleId > 0:
			self.base.requestEnterGame()
	
	def verifySuccess( self ):
		self.base.login( self.m_RoleId, "" )
	
	def deleteRoleCB( self, roleID ) :
		"""
		删除一个角色
		@type					roleID : INT64
		@param					roleID : 被删除的角色数据库 ID
		"""
		#roleSelector.onDeleteRole( roleID )

	# ----------------------------------------------------------------
	# called by client
	# ----------------------------------------------------------------
	def isPlayer( self ) :
		"""
		指出是否是玩家
		@type					: bool
		@return					: 总是返回 False，表示不是 PlayerRole
		"""
		return False

	def timeSynchronization( self, serverTime ):
		"""
		同步服务器时间
		@type				serverTime : float
		@param				serverTime : 服务器时间
		"""
		pass
	
	def receiveWattingTime( self, order, waitTime ):
		"""
		Define method.
		接收等待登录的时间
		"""
		pass
	
	# -------------------------------------------------
	def onAccountLogin( self ) :
		"""
		Define method.
		登录游戏成功，加载角色选择场景
		"""
		pass
