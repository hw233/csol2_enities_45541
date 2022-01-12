# -*- coding: gb18030 -*-

"""
"""

import random
import Language
import Love3
import csdefine
import csstatus
from bwdebug import *
from GameObject import GameObject
from SpaceCopyTeam import SpaceCopyTeam

class SpaceCopyExpMelee( SpaceCopyTeam ):
	"""
	�����Ҷ��ű�
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopyTeam.__init__( self )

	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		SpaceCopyTeam.load( self, section )
		data = section[ "Space" ][ "playerEnterPoint" ]
		self._playerEnterPoint = ( eval( data[ "pos" ].asString ), eval( data[ "direction" ].asString ) )

	def onSpaceTeleportEntity( self, selfEntity, position, direction, baseMailbox, pickData  ):
		"""
		domain�ҵ���Ӧ��spaceNormal��spaceNormal��ʼ����һ��entity������space��ʱ��֪ͨ
		"""
		SpaceCopyTeam.onSpaceTeleportEntity( self, selfEntity, self._playerEnterPoint[0], self._playerEnterPoint[1], baseMailbox, pickData )
		
# SpaceCopyPotential.py
