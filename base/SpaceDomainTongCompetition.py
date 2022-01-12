# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
from SpaceDomainCopy import SpaceDomainCopy
import csdefine
spaceItems = None

class SpaceDomainTongCompetition( SpaceDomainCopy ):
	"""
	���徺��
	"""
	def __init__( self ):
		"""
		"""
		SpaceDomainCopy.__init__( self )	
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS	
	
	def removeSpaceItem( self, spaceNumber ):
		"""
		virtual method.
		ģ�巽����ɾ��spaceItem
		"""
		self.keyToSpaceNumber.clear()
		SpaceDomainCopy.removeSpaceItem( self, spaceNumber )

	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		"""
		baseMailbox.logonSpaceInSpaceCopy()

	
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
		spaceItem = self.findSpaceItem( params, True )
			
		tongCompetitionMgr = BigWorld.globalData["TongCompetitionMgr"]
		tongCompetitionMgr.teleportEntity(self, spaceItem.baseMailbox, position, direction, baseMailbox, params)
	
	def onSpaceItemEnter( self, position, direction, baseMailbox, params ):
		spaceItem = self.findSpaceItem( params, True )
		try:
			pickData = self.pickToSpaceData( baseMailbox, params )
			spaceItem.enter( baseMailbox, position, direction, pickData )
		except:
			ERROR_MSG( "%s teleportEntity is error." % self.name )