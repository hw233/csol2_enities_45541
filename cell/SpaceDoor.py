# -*- coding: gb18030 -*-
#
# $Id: SpaceDoor.py,v 1.20 2008-08-07 08:15:50 phw Exp $

"""
切换点实体。
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
	出入口实体，提供玩家角色切换场景的操作。
		@ivar destSpace:	目标场景标识
		@type destSpace:	string
		@ivar destPosition:	目标点坐标
		@type destPosition:	vector3
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		GameObject.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_SPACE_DOOR )
		if self.useRectangle:
			#对于矩形传送门，直接采用 长和宽的和的一半来处理
			width, height, long = self.volume
			self.radius = ( width + long )/2.0

		if len( self.destSpace ) == 0:
			self.destSpace = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
			INFO_MSG( "%s(%i): I have no dest space, use default." % (self.className, self.id), self.destSpace )
		# 以下是转换direction的格式（游戏中要把地编中的坐标的第2跟第3位坐标互换，而且把角度转成孤度会精确点）
		self.destDirection = ( self.destDirection[0], self.destDirection[2], self.destDirection[1] * math.pi / 180 )

	def enterDoor( self, srcEntityID ):
		"""
		Exposed method.
		进入切换点
		"""
		if self.enterDoorCheck( srcEntityID ) :
			role = BigWorld.entities[ srcEntityID ]
			self.onEnterDoor( role )
	
	def enterDoorCheck( self, roleID ):
		"""
		进入切换点合法性检查
		"""
		role = BigWorld.entities.get( roleID, None )
		if not role :
			INFO_MSG( "entity %i not exist in world" % roleID )		# 这个应该永远都不可能到达
			return False
		if self.position.flatDistTo( role.position ) > self.radius + 1 : 	# 由于延时我们在范围这里加大1米
			WARNING_MSG( "%s(%i): target too far." % ( role.playerName, role.id ) )
			return False
		
		return True
	
	def onEnterDoor( self, role ):
		"""
		玩家进入传送门处理
		"""
		role.beforeEnterSpaceDoor( self.destPosition, self.destDirection )
		role.gotoSpace( self.destSpace, self.destPosition, self.destDirection )
	
	def requestDestination( self, srcEntityID ):
		"""
		Exposed method.
		请求目的地信息
		"""
		try:
			BigWorld.entities[ srcEntityID ].clientEntity( self.id ).receiverDestination( self.destSpace, self.destPosition )
		except:
			HACK_MSG( "cant find entity( %i ), entity may be destroyed!" )

# SpaceDoor.py
