# -*- coding: gb18030 -*-

from bwdebug import *
from SpaceDomain import SpaceDomain
import csdefine

class SpaceDomainCityWarFinal( SpaceDomain ):
	"""
	�����ս�������� 
	"""
	def __init__( self ):
		SpaceDomain.__init__(self)
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS

	def teleportEntity( self, position, direction, baseMailbox, params ):
		"""
		define method.
		����һ��entity��ָ����space��
		"""
		BigWorld.globalData[ "TongManager" ].onEnterCityWarFinalSpace( self, baseMailbox, params )

	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		define method
		��½����
		"""
		baseMailbox.logonSpaceInSpaceCopy()

	def onRoleEnterSpace( self, baseMailbox, params ):
		"""
		define method
		����������ռ�
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: role %i request enter space params is %s" % ( baseMailbox.id, params ) )
		spaceItem = self.findSpaceItem( params, True )

		enterPos = self.getScript().getEnterPos( params.get( "enterPos" ) )
		pos, dir = enterPos[ :3 ], enterPos[ 3 :]
		pickData = self.pickToSpaceData( baseMailbox, params )
		spaceItem.enter( baseMailbox, pos, dir, pickData )