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
		������븱��
		"""
		enterCopyNo  = params.get( "enterCopyNo", 0 )
		isCreate = self._NoToSpaceItem.has_key( enterCopyNo )
		membersMailboxs = params.pop( "membersMailboxs", [] )
		spaceItem = self.findSpaceItem( enterCopyNo, params, True )
		try:
			pickData = domain.pickToSpaceData( baseMailbox, params )
			spaceItem.enter( baseMailbox, position, direction, pickData )
			if len( membersMailboxs ) and not isCreate: # Ŀǰ��˵���Ѿ������ľɵ�ͼӦ���ǲ���һ���Ͷ�Ա��
				self.transmitMember( position, direction, baseMailbox, membersMailboxs, params )
		except:
			ERROR_MSG( "%s copy item enter is error." % self._domain.getSpaceClassName( params ) )
	
	def transmitMember( self, position, direction, baseMailbox, membersMailboxs, params ):
		"""
		����������
		"""
		for membersMailbox in membersMailboxs:
			if membersMailbox.id != baseMailbox.id:
				membersMailbox.cell.gotoSpace( self._domain.getSpaceClassName( params ), position, direction )	# �����ж�ԱҲ���͵�������
	
	def logon( self, baseMailbox, params ):
		"""
		��ҵ�½
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
		�رո���
		"""
		self.isDestroy = True
		for spaceItem in self._NoToSpaceItem.values():
			spaceItem.baseMailbox.cell.onCloseMapsCopy( )
			
	def findSpaceItem( self, enterNo, params = {}, createIfNotExisted = False ):
		"""
		����spaceItem
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
		������BOSS����ɱ
		"""
		self._copyStatBoss += 1
		for item in self._NoToSpaceItem.values():
			item.baseMailbox.cell.setCopyKillBoss( self._copyStatBoss )
	
	def killCopyMonster( self ):
		"""
		����С�ֱ���ɱ
		"""
		self._copyStatMonster += 1
		for item in self._NoToSpaceItem.values():
			item.baseMailbox.cell.setCopyKillMonster( self._copyStatMonster )
	
	def allCopyMonsterkilled( self, spaceName ):
		"""
		������С��ȫ������ɱ
		"""
		for item in self._NoToSpaceItem.values():
			item.baseMailbox.cell.onAllCopyMonsterkilled( spaceName )
		
class SpaceDomainCopyMaps( SpaceDomain, UseDomainForTeamInter ):
	# ���ͼ����
	def __init__( self ):
		SpaceDomain.__init__( self )
		UseDomainForTeamInter.__init__( self )
		self._copyItem = {}
	
	def getSpaceClassName( self, params ):
		"""
		��ȡspace className
		"""
		return params[ "enterCopyKey" ]
	
	def _getCoyKeyFromParams( self, params ):
		"""
		�Ӳ��������ȡ������key
		"""
		return params.get( "dbID" )
	
	def createNewItem( self, key ):
		return CopyItem( self, key )
	
	def findCoyItem( self, key ):
		"""
		ͨ��dbid ȡ��copy item
		"""
		return self._copyItem.get( key, None )
	
	def findCoyItemOrCreate( self, key ):
		"""
		����copy item ���û���򴴽�
		"""
		copyItem  = self.findCoyItem( key )
		if not copyItem:
			copyItem = self.createNewItem( key )
			self._copyItem[ key ] = copyItem
		
		return copyItem
	
	def teleportEntity( self, position, direction, baseMailbox, params ):
		"""
		define method.
		����һ��entity��ָ����space��
		@type position : VECTOR3, 
		@type direction : VECTOR3, 
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: һЩ���ڸ�entity����space�Ķ�������� (domain����)
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
		��������µ�¼��ʱ�򱻵��ã������������ָ����space�г��֣�һ�������Ϊ���������ߵĵ�ͼ����
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: һЩ���ڸ�entity����space�Ķ��������(domain����)
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
		�ر�ָ������
		"""
		copyKey = self._getCoyKeyFromParams( params )
		copyItem = self.findCoyItem( copyKey )
		if copyItem:
			copyItem.closeCopyItem( params )
			#del self._copyItem[ copyKey ]

	def removeSpaceItem( self, spaceNumber ):
		"""
		virtual method.
		ģ�巽����ɾ��spaceItem
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
		������boss����ɱ
		"""
		if self._copyItem.has_key( copyKey ):
			self._copyItem[ copyKey ].killCopyBoss()
	
	def killCopyMonster( self, copyKey ):
		"""
		define method
		������boss����ɱ
		"""
		if self._copyItem.has_key( copyKey ):
			self._copyItem[ copyKey ].killCopyMonster()

	def allCopyMonsterkilled( self, copyKey, spaceName ):
		"""
		define method
		������С��ȫ������ɱ����Ҫ����������󸱱���
		"""
		if self._copyItem.has_key( copyKey ):
			self._copyItem[ copyKey ].allCopyMonsterkilled( spaceName )