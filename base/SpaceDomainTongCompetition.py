# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
from SpaceDomainCopy import SpaceDomainCopy
import csdefine
spaceItems = None

class SpaceDomainTongCompetition( SpaceDomainCopy ):
	"""
	家族竞赛
	"""
	def __init__( self ):
		"""
		"""
		SpaceDomainCopy.__init__( self )	
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS	
	
	def removeSpaceItem( self, spaceNumber ):
		"""
		virtual method.
		模板方法；删除spaceItem
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
		传送一个entity到指定的space中
		@type position : VECTOR3, 
		@type direction : VECTOR3, 
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: 一些关于该entity进入space的额外参数； (domain条件)
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