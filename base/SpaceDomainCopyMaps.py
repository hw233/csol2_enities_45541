# -*- coding: gb18030 -*-
import time
from bwdebug import *
from SpaceDomain import SpaceDomain
from interface.DomainTeamInterface import UseDomainForTeamInter

class CopyItem( object ):
	def __init__( self, domain, key ):
		object.__init__( self )
		self.createTime  = time.time()
		self._domain = domain
		self.copyKey = key
		self._NoToSpaceItem = {}
		
		self._copyStatBoss = 0
		self._copyStatMonster = 0
		
		self.isDestroy = False
		
	def enter( self, domain, position, direction, baseMailbox, params ):
		"""
		申请进入副本
		"""
		enterCopyNo  = params.get( "enterCopyNo", 0 )
		isCreate = self._NoToSpaceItem.has_key( enterCopyNo )
		membersMailboxs = params.pop( "membersMailboxs", [] )
		spaceItem = self.findSpaceItem( enterCopyNo, params, True )
		try:
			pickData = domain.pickToSpaceData( baseMailbox, params )
			spaceItem.enter( baseMailbox, position, direction, pickData )
			if len( membersMailboxs ) and not isCreate: # 目前来说，已经创建的旧地图应该是不会一起传送队员的
				self.transmitMember( position, direction, baseMailbox, membersMailboxs, params )
		except:
			ERROR_MSG( "%s copy item enter is error." % self._domain.getSpaceClassName( params ) )
	
	def transmitMember( self, position, direction, baseMailbox, membersMailboxs, params ):
		"""
		传送其它人
		"""
		for membersMailbox in membersMailboxs:
			if membersMailbox.id != baseMailbox.id:
				membersMailbox.cell.gotoSpace( self._domain.getSpaceClassName( params ), position, direction )	# 把所有队员也传送到副本中
	
	def logon( self, baseMailbox, params ):
		"""
		玩家登陆
		"""
		enterCopyNo  = params.get( "enterCopyNo", 0 )
		spaceItem  = self.findSpaceItem( enterCopyNo )
		spaceItem.logon( baseMailbox )
	
	def removeSpaceItem( self, spaceNumber ):
		for k, i in self._NoToSpaceItem.items():
			if i.spaceNumber == spaceNumber:
				del self._NoToSpaceItem[ k ]
				return True
				
		return False
	
	def closeCopyItem( self, params ):
		"""
		关闭副本
		"""
		self.isDestroy = True
		for spaceItem in self._NoToSpaceItem.values():
			spaceItem.baseMailbox.cell.onCloseMapsCopy( )
			
	def findSpaceItem( self, enterNo, params = {}, createIfNotExisted = False ):
		"""
		创建spaceItem
		"""
		if self._NoToSpaceItem.has_key( enterNo ):
			return self._NoToSpaceItem[ enterNo ]
				
		if createIfNotExisted:
			params[ "createTime" ] = self.createTime
			params[ "copyKey" ] = self.copyKey
			params[ "copyStatBoss" ] = self._copyStatBoss
			params[ "copyStatMonster" ] = self._copyStatMonster
			spaceItem = self._domain.createSpaceItem( params )
			self._NoToSpaceItem[ enterNo ] = spaceItem
			return spaceItem
		
		return None
	
	def killCopyBoss( self ):
		"""
		副本的BOSS被击杀
		"""
		self._copyStatBoss += 1
		for item in self._NoToSpaceItem.values():
			item.baseMailbox.cell.setCopyKillBoss( self._copyStatBoss )
	
	def killCopyMonster( self ):
		"""
		副本小怪被击杀
		"""
		self._copyStatMonster += 1
		for item in self._NoToSpaceItem.values():
			item.baseMailbox.cell.setCopyKillMonster( self._copyStatMonster )
	
	def allCopyMonsterkilled( self, spaceName ):
		"""
		副本中小怪全部被击杀
		"""
		for item in self._NoToSpaceItem.values():
			item.baseMailbox.cell.onAllCopyMonsterkilled( spaceName )
		
class SpaceDomainCopyMaps( SpaceDomain, UseDomainForTeamInter ):
	# 多地图副本
	def __init__( self ):
		SpaceDomain.__init__( self )
		UseDomainForTeamInter.__init__( self )
		self._copyItem = {}
	
	def getSpaceClassName( self, params ):
		"""
		获取space className
		"""
		return params[ "enterCopyKey" ]
	
	def _getCoyKeyFromParams( self, params ):
		"""
		从参数里面获取副本的key
		"""
		return params.get( "dbID" )
	
	def createNewItem( self, key ):
		return CopyItem( self, key )
	
	def findCoyItem( self, key ):
		"""
		通过dbid 取得copy item
		"""
		return self._copyItem.get( key, None )
	
	def findCoyItemOrCreate( self, key ):
		"""
		查找copy item 如果没有则创建
		"""
		copyItem  = self.findCoyItem( key )
		if not copyItem:
			copyItem = self.createNewItem( key )
			self._copyItem[ key ] = copyItem
		
		return copyItem
	
	def teleportEntity( self, position, direction, baseMailbox, params ):
		"""
		define method.
		传送一个entity到指定的space中
		@type position : VECTOR3, 
		@type direction : VECTOR3, 
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: 一些关于该entity进入space的额外参数； (domain条件)
		@type params : PY_DICT = None
		"""
		copyKey = self._getCoyKeyFromParams( params )
		copyItem = self.findCoyItemOrCreate( copyKey )
		try:
			copyItem.enter( self, position, direction, baseMailbox, params )
		except:
			ERROR_MSG( "%s teleportEntity is error." % self.getSpaceClassName(params) )
	
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		define method.
		在玩家重新登录的时候被调用，用于让玩家在指定的space中出现（一般情况下为玩家最后下线的地图）；
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: 一些关于该entity进入space的额外参数；(domain条件)
		@type params : PY_DICT = None
		"""
		copyKey = self._getCoyKeyFromParams( params )
		copyItem = self.findCoyItem( copyKey )
		if copyItem:
			copyItem.logon( baseMailbox, params )
		else:
			baseMailbox.logonSpaceInSpaceCopy()
		
	def closeCopyItem( self, params ):
		"""
		define method
		关闭指定副本
		"""
		copyKey = self._getCoyKeyFromParams( params )
		copyItem = self.findCoyItem( copyKey )
		if copyItem:
			copyItem.closeCopyItem( params )
			#del self._copyItem[ copyKey ]

	def removeSpaceItem( self, spaceNumber ):
		"""
		virtual method.
		模板方法；删除spaceItem
		"""
		delItem = 0
		for item in self._copyItem.values():
			if item.removeSpaceItem( spaceNumber ):
				delItem = item
				break
				
		if delItem and delItem.isDestroy:
			del self._copyItem[ delItem.copyKey ]
		
		SpaceDomain.removeSpaceItem( self, spaceNumber )
	
	def killCopyBoss( self, copyKey ):
		"""
		define method
		副本的boss被击杀
		"""
		if self._copyItem.has_key( copyKey ):
			self._copyItem[ copyKey ].killCopyBoss()
	
	def killCopyMonster( self, copyKey ):
		"""
		define method
		副本的boss被击杀
		"""
		if self._copyItem.has_key( copyKey ):
			self._copyItem[ copyKey ].killCopyMonster()

	def allCopyMonsterkilled( self, copyKey, spaceName ):
		"""
		define method
		副本中小怪全部被击杀，主要用于摄魂迷阵副本中
		"""
		if self._copyItem.has_key( copyKey ):
			self._copyItem[ copyKey ].allCopyMonsterkilled( spaceName )