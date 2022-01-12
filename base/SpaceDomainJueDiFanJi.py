# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
from SpaceDomain import SpaceDomain
import csdefine

class SpaceDomainJueDiFanJi( SpaceDomain ):
	"""
	���ط���
	"""
	def __init__( self ):
		"""
		"""
		SpaceDomain.__init__( self )
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS

	def onSpaceCloseNotify( self, spaceNumber ):
		"""
		define method.
		�ռ�رգ�space entity����֪ͨ��
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
		#����һ��entity��ָ����space��

		BigWorld.globalData[ "JueDiFanJiMgr" ].onEnterJueDiFanJiSpace( self, baseMailbox, params )
		
	def onEnterSpace( self, baseMailbox, params ):
		"""
		define method
		��ҽ�����ط��������
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
			#������µ�¼
			spaceItem = self.findSpaceItem( params, False )
			
			if not spaceItem:
				baseMailbox.logonSpaceInSpaceCopy()
			else:
				spaceItem.logon()
		pass
		