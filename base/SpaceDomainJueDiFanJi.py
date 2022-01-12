# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
from SpaceDomain import SpaceDomain
import csdefine

class SpaceDomainJueDiFanJi( SpaceDomain ):
	"""
	绝地反击
	"""
	def __init__( self ):
		"""
		"""
		SpaceDomain.__init__( self )
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS

	def onSpaceCloseNotify( self, spaceNumber ):
		"""
		define method.
		空间关闭，space entity销毁通知。
		@param 	spaceNumber		:		spaceNumber
		@type 	spaceNumber		:		int32
		"""
		SpaceDomain.onSpaceCloseNotify( self, spaceNumber )

	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		"""
		params[ "login" ] = True
		BigWorld.globalData[ "JueDiFanJiMgr" ].onEnterJueDiFanJiSpace( self, baseMailbox, params )
		
	def teleportEntity( self, position, direction, baseMailbox, params ):
		#define method.
		#传送一个entity到指定的space中

		BigWorld.globalData[ "JueDiFanJiMgr" ].onEnterJueDiFanJiSpace( self, baseMailbox, params )
		
	def onEnterSpace( self, baseMailbox, params ):
		"""
		define method
		玩家进入绝地反击活动副本
		"""
		DEBUG_MSG( "params=",  params )
		isLogin = params.has_key( "login" )
		if not isLogin:
			spaceItem = self.findSpaceItem( params, True )
			
			position = (0, 0, 0)
			direction = (0, 0, 0)
			if params[ "left" ] == params[ "dbID" ]:
				position, direction = self.getScript().left_playerEnterPoint
			elif params[ "right" ] == params[ "dbID" ]:
				position, direction = self.getScript().right_playerEnterPoint
			if spaceItem:
				pickData = self.pickToSpaceData( baseMailbox, params )
				spaceItem.enter( baseMailbox, position, direction, pickData )
		else:
			#玩家重新登录
			spaceItem = self.findSpaceItem( params, False )
			
			if not spaceItem:
				baseMailbox.logonSpaceInSpaceCopy()
			else:
				spaceItem.logon()
		pass
		