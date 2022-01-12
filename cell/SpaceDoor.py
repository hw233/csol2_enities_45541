# -*- coding: gb18030 -*-
#
# $Id: SpaceDoor.py,v 1.20 2008-08-07 08:15:50 phw Exp $

"""
�л���ʵ�塣
"""

import BigWorld
import Role
from bwdebug import *
from interface.GameObject import GameObject
import csdefine
import csconst
import math
import csstatus
from TimeString import TimeString

class SpaceDoor(GameObject):
	"""
	�����ʵ�壬�ṩ��ҽ�ɫ�л������Ĳ�����
		@ivar destSpace:	Ŀ�곡����ʶ
		@type destSpace:	string
		@ivar destPosition:	Ŀ�������
		@type destPosition:	vector3
	"""
	def __init__(self):
		"""
		���캯����
		"""
		GameObject.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_SPACE_DOOR )
		if self.useRectangle:
			#���ھ��δ����ţ�ֱ�Ӳ��� ���Ϳ�ĺ͵�һ��������
			width, height, long = self.volume
			self.radius = ( width + long )/2.0

		if len( self.destSpace ) == 0:
			self.destSpace = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
			INFO_MSG( "%s(%i): I have no dest space, use default." % (self.className, self.id), self.destSpace )
		# ������ת��direction�ĸ�ʽ����Ϸ��Ҫ�ѵر��е�����ĵ�2����3λ���껥�������ҰѽǶ�ת�ɹ¶Ȼᾫȷ�㣩
		self.destDirection = ( self.destDirection[0], self.destDirection[2], self.destDirection[1] * math.pi / 180 )

	def enterDoor( self, srcEntityID ):
		"""
		Exposed method.
		�����л���
		"""
		if self.enterDoorCheck( srcEntityID ) :
			role = BigWorld.entities[ srcEntityID ]
			self.onEnterDoor( role )
	
	def enterDoorCheck( self, roleID ):
		"""
		�����л���Ϸ��Լ��
		"""
		role = BigWorld.entities.get( roleID, None )
		if not role :
			INFO_MSG( "entity %i not exist in world" % roleID )		# ���Ӧ����Զ�������ܵ���
			return False
		if self.position.flatDistTo( role.position ) > self.radius + 1 : 	# ������ʱ�����ڷ�Χ����Ӵ�1��
			WARNING_MSG( "%s(%i): target too far." % ( role.playerName, role.id ) )
			return False
		
		return True
	
	def onEnterDoor( self, role ):
		"""
		��ҽ��봫���Ŵ���
		"""
		role.beforeEnterSpaceDoor( self.destPosition, self.destDirection )
		role.gotoSpace( self.destSpace, self.destPosition, self.destDirection )
	
	def requestDestination( self, srcEntityID ):
		"""
		Exposed method.
		����Ŀ�ĵ���Ϣ
		"""
		try:
			BigWorld.entities[ srcEntityID ].clientEntity( self.id ).receiverDestination( self.destSpace, self.destPosition )
		except:
			HACK_MSG( "cant find entity( %i ), entity may be destroyed!" )

# SpaceDoor.py
