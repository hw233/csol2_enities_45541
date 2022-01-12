# -*- coding: gb18030 -*-

from bwdebug import *
from SpaceDomain import SpaceDomain
import csdefine

class SpaceDomainCityWarFinal( SpaceDomain ):
	"""
	帮会夺城战副本领域 
	"""
	def __init__( self ):
		SpaceDomain.__init__(self)
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS

	def teleportEntity( self, position, direction, baseMailbox, params ):
		"""
		define method.
		传送一个entity到指定的space中
		"""
		BigWorld.globalData[ "TongManager" ].onEnterCityWarFinalSpace( self, baseMailbox, params )

	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		define method
		登陆传送
		"""
		baseMailbox.logonSpaceInSpaceCopy()

	def onRoleEnterSpace( self, baseMailbox, params ):
		"""
		define method
		玩家请求进入空间
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: role %i request enter space params is %s" % ( baseMailbox.id, params ) )
		spaceItem = self.findSpaceItem( params, True )

		enterPos = self.getScript().getEnterPos( params.get( "enterPos" ) )
		pos, dir = enterPos[ :3 ], enterPos[ 3 :]
		pickData = self.pickToSpaceData( baseMailbox, params )
		spaceItem.enter( baseMailbox, pos, dir, pickData )