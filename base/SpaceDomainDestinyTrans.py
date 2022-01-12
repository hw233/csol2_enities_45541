# -*- coding: gb18030 -*-

import csdefine
from bwdebug import *
from SpaceDomainCopyTeam import SpaceDomainCopyTeam

class SpaceDomainDestinyTrans( SpaceDomainCopyTeam ):
	"""
	天命轮回副本
	"""
	def __init__( self ):
		SpaceDomainCopyTeam.__init__( self )

	def teleportEntity( self, pos, dir, baseMailbox, params ):
		"""
		define method.
		玩家进入关卡
		"""
		spaceItem = self.findSpaceItem( params, True )
		try:
			pickData = self.pickToSpaceData( baseMailbox, params )
			spaceItem.enter( baseMailbox, pos, dir, pickData )
		except:
			ERROR_MSG( "%s teleportEntity is error." % self.name )