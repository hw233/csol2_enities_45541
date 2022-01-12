# -*- coding: gb18030 -*-
import BigWorld

import cschannel_msgs
import csstatus
from bwdebug import *

INIT_INTEGRAL = 5

class BattlefieldMember( object ):
	"""
	对战数据基类
	"""
	def __init__( self, roleID = 0, roleName = "", roleMB = None, kill = 0, bekill = 0, integral = 0  ):
		object.__init__( self )
		self.roleID = roleID
		self.roleName = roleName
		self.roleMB = roleMB
		self.kill = kill
		self.bekill = bekill
		self.integral = integral
		if self.roleMB:
			self.upInfos()
	
	def initData( self, dict ):
		self.roleID = dict[ "roleID" ]
		self.roleName = dict[ "roleName" ]
		self.roleMB = dict[ "roleMB" ]
		self.kill = dict[ "kill" ]
		self.bekill = dict[ "bekill" ]
		self.integral = dict[ "integral" ]
	
	def addIntegral( self, integral ):
		self.integral += integral
		self.upInfos()
	
	def decIntegral( self, integral ):
		self.integral -= integral
		self.upInfos()
	
	def onDie( self ):
		self.bekill += 1
	
	def onKill( self ):
		self.kill += 1
	
	def upInfos( self ):
		pass
	
	def getDictFromObj( self, obj ):
		dict = {
			"roleID" 	: obj.roleID,
			"roleName"	: obj.roleName,
			"roleMB"	: obj.roleMB,
			"kill" 		: obj.kill,
			"bekill"	: obj.bekill,
			"integral" 	: obj.integral
		}
		return dict
	
	def createObjFromDict( self, dict ):
		obj = BattlefieldMember()
		obj.initData( dict )
		return obj
		
	def isSameType( self, obj ):
		return isinstance( obj, BattlefieldMember )

class FengQiMember( BattlefieldMember ):
	"""
	夜战凤栖战场成员数据
	"""
	def __init__( self, roleID = 0, roleName = "", roleMB = None, kill = 0, bekill = 0, integral = 0, box = 0  ):
		BattlefieldMember.__init__( self )
		self.roleID = roleID
		self.roleName = roleName
		self.roleMB = roleMB
		self.kill = kill
		self.bekill = bekill
		self.integral = integral
		self.box = box
	
	def addBox( self ):
		self.box += 1
	
	def initData( self, dict ):
		self.roleID = dict[ "roleID" ]
		self.roleName = dict[ "roleName" ]
		self.roleMB = dict[ "roleMB" ]
		self.kill = dict[ "kill" ]
		self.bekill = dict[ "bekill" ]
		self.integral = dict[ "integral" ]
		self.box = dict[ "box" ]
	
	def getDictFromObj( self, obj ):
		dict = {
			"roleID" 	: obj.roleID,
			"roleName"	: obj.roleName,
			"roleMB"	: obj.roleMB,
			"kill" 		: obj.kill,
			"bekill"	: obj.bekill,
			"integral" 	: obj.integral,
			"box"		: obj.box,
		}
		return dict
	
	def createObjFromDict( self, dict ):
		obj = FengQiMember()
		obj.initData( dict )
		return obj
		
	def isSameType( self, obj ):
		return isinstance( obj, FengQiMember )

class BattlefieldMemberMgr( object ):
	"""
	战场成员数据管理器
	"""
	def __init__( self ):
		object.__init__( self )
		self.members = {}
	
	def initData( self, dict ):
		for m  in dict[ "members" ]:
			self.members[ m.roleID ] = m
			
	def add( self, roleMB, roleName, kill = 0, bekill = 0, integral = INIT_INTEGRAL ):
		self.members[ roleMB.id ] = BattlefieldMember( roleMB.id, roleName, roleMB, kill, bekill, integral )
	
	def remove( self, playerMB ):
		if self.members.has_key( playerMB.id ):
			del self.members[ playerMB.id ]
	
	def addIntegral( self, roleID, integral ):
		if self.members.has_key( roleID ):
			self.members[ roleID ].addIntegral( integral )
	
	def decIntegral( self, roleID, integral ):
		if self.members.has_key( roleID ):
			self.members[ roleID ].decIntegral( integral )
	
	def getIntegral( self, roleID ):
		if self.members.has_key( roleID ):
			return self.members[ roleID ].integral
			
		return 0
	
	def getDictFromObj( self, obj ):
		dict = {}
		dict[ "members" ] = obj.members.values()
		return dict
	
	def createObjFromDict( self, dict ):
		obj = BattlefieldMemberMgr()
		obj.initData( dict )
		return obj
		
	def isSameType( self, obj ):
		return isinstance( obj, BattlefieldMemberMgr )

class FengQiMemberMgr( BattlefieldMemberMgr ):
	"""
	夜战凤栖战场成员数据管理器
	"""
	def add( self, roleMB, roleName, kill = 0, bekill = 0, integral = INIT_INTEGRAL ):
		m = FengQiMember( roleMB.id, roleName, roleMB, kill, bekill, integral )
		self.members[ roleMB.id ] = m
		self.upInfoAllToClient( m )
		self.upInfoToClients( m )
		self.upIntegralToClients( m )
		self.upIntegralAllToClient( m )
		self.upBoxAllToClient( m )
	
	def remove( self, playerMB ):
		BattlefieldMemberMgr.remove( self, playerMB )
		playerMB.client.fengQiOnExit()
		for m in self.members.itervalues():
			m.roleMB.client.fengQiExitMember( playerMB.id )
	
	def addIntegral( self, roleID, integral ):
		if self.members.has_key( roleID ):
			m = self.members[ roleID ]
			m.addIntegral( integral )
			self.upIntegralToClients( m )
	
	def decIntegral( self, roleID, integral ):
		if self.members.has_key( roleID ):
			m = self.members[ roleID ]
			m.decIntegral( integral )
			self.upIntegralToClients( m )
		
	def kill( self, killer, dead ):
		if self.members.has_key( killer ):
			k = self.members[ killer ]
			k.onKill()
			self.upInfoToClients( k )
			
		if self.members.has_key( dead ):
			d = self.members[ dead ]
			d.onDie()
			self.upInfoToClients( d )
		
	def addBox( self, roleID ):
		if self.members.has_key( roleID ):
			m = self.members[ roleID ]
			m.addBox()
			self.upBoxToClients( m )
		
	def onAcitivyEnd( self, pMB ):
		pMB.cell.fengQiOnExit()
	
	def upInfoToClients( self, upMember ):
		for m in self.members.itervalues():
			m.roleMB.client.fengQiUpReport( upMember.roleID, upMember.roleName, upMember.kill, upMember.bekill )
	
	def upInfoAllToClient( self, upMember ):
		for m in self.members.itervalues():
			upMember.roleMB.client.fengQiUpReport( m.roleID, m.roleName, m.kill, m.bekill )
	
	def upIntegralToClients( self, upMember ):
		for m in self.members.itervalues():
			m.roleMB.client.fengQiUpIntegral( upMember.roleID, upMember.integral )
	
	def upIntegralAllToClient( self, upMember ):
		for m in self.members.itervalues():
			upMember.roleMB.client.fengQiUpIntegral( m.roleID, m.integral )
		
	def upBoxToClients( self, upMember ):
		for m in self.members.itervalues():
			m.roleMB.client.fengQiUpBox( upMember.roleID, upMember.box )
			
	def upBoxAllToClient( self, upMember ):
		for m in self.members.itervalues():
			upMember.roleMB.client.fengQiUpBox( m.roleID, m.box )
	
	def createObjFromDict( self, dict ):
		obj = FengQiMemberMgr()
		obj.initData( dict )
		return obj
	
	def isSameType( self, obj ):
		return isinstance( obj, FengQiMemberMgr )
		
g_fengQiMemberIns = FengQiMember()
g_FengQiMemberMgrIns = FengQiMemberMgr()
		