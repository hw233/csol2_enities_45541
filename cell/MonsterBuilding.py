# -*- coding: gb18030 -*-
# 建筑物类型的怪物，没有坐标移动

from Monster import Monster
from bwdebug import *
import csconst
import csdefine
import ECBExtend
import BigWorld
import math
import Const
VOLATILE_INFO_CLOSED = (BigWorld.VOLATILE_NEVER,) * 4

class MonsterBuilding( Monster ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
		self.volatileInfo = VOLATILE_INFO_CLOSED
		
		
	def openVolatileInfo( self ):
		"""
		virtual method.
		打开坐标信息传送功能
		"""
		pass

	def closeVolatileInfo( self ):
		"""
		virtual method.
		关闭坐标信息传送功能
		"""
		pass
		
	def moveToPosFC( self, endDstPos, targetMoveSpeed, targetMoveFace ):
		"""
		连击移动
		"""
		pass
		
	def distanceBB( self, destEntity ):
		"""
		计算与目标entity的boundingbox边界之间的3D坐标系的距离
		@return: float
		"""
		# 当前直接以bounding box的宽的一半作为bounding box的中心到边界的距离
		s1 = self.getBoundingBox().z / 2
		s2 = self.getBoundingBox().x / 2
		off_A = math.atan(s2/s1)
		off_dis = s2 / math.sin(off_A)
		d1 = destEntity.getBoundingBox().z / 2
		yaw1 = self.yaw
		yaw2 = ( self.position - destEntity.position ).yaw
		disYaw = abs( yaw1 - yaw2 )
		if disYaw + off_A >=  math.pi*2: #在第一象限内 
			disYaw = disYaw - math.pi*2
		disYaw = abs( disYaw )
		if  0 <= disYaw <= off_A or  math.pi - off_A <= disYaw <= math.pi + off_A: #正面
			dis =  s1 / abs( math.cos( disYaw ) )
		else: #侧面
			dis =  s2 / abs( math.sin( disYaw-math.pi ) )
		if dis >= off_dis:
			dis = off_dis
		return self.position.distTo( destEntity.position ) - dis - d1
	
	def onWitnessed( self, isWitnessed ):
		"""
		see also Python Cell API::Entity::onWitnessed()
		@param isWitnessed: A boolean indicating whether or not the entity is now witnessed;
		@type  isWitnessed: bool
		"""
		Monster.onWitnessed( self, isWitnessed )
		self.spellTarget( Const.ENTITY_CREATE_TRIGGER_SKILL_ID , self.id )
