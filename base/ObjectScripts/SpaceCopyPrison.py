# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyPrison.py,v 1.2 2008-08-28 00:52:47 kebiao Exp $

"""
"""
import BigWorld
from bwdebug import *
from SpaceMultiLine import SpaceMultiLine

class SpaceCopyPrison( SpaceMultiLine ):
	"""
	����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceMultiLine.__init__( self )

	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		SpaceMultiLine.load( self, section )
		data = section[ "Space" ][ "doorPoint" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		
		self.enterPoint = ( pos, direction )
		
	def onSpaceTeleportEntity( self, selfEntity, position, direction, baseMailbox, pickData ):
		"""
		domain�ҵ���Ӧ��spaceNormal��spaceNormal��ʼ����һ��entity������space��ʱ��֪ͨ
		"""
		baseMailbox.cell.teleportToSpace( self.enterPoint[0], self.enterPoint[1], selfEntity.cell, selfEntity.spaceID )
		
