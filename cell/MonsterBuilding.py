# -*- coding: gb18030 -*-
# ���������͵Ĺ��û�������ƶ�

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
		��������Ϣ���͹���
		"""
		pass

	def closeVolatileInfo( self ):
		"""
		virtual method.
		�ر�������Ϣ���͹���
		"""
		pass
		
	def moveToPosFC( self, endDstPos, targetMoveSpeed, targetMoveFace ):
		"""
		�����ƶ�
		"""
		pass
		
	def distanceBB( self, destEntity ):
		"""
		������Ŀ��entity��boundingbox�߽�֮���3D����ϵ�ľ���
		@return: float
		"""
		# ��ǰֱ����bounding box�Ŀ��һ����Ϊbounding box�����ĵ��߽�ľ���
		s1 = self.getBoundingBox().z / 2
		s2 = self.getBoundingBox().x / 2
		off_A = math.atan(s2/s1)
		off_dis = s2 / math.sin(off_A)
		d1 = destEntity.getBoundingBox().z / 2
		yaw1 = self.yaw
		yaw2 = ( self.position - destEntity.position ).yaw
		disYaw = abs( yaw1 - yaw2 )
		if disYaw + off_A >=  math.pi*2: #�ڵ�һ������ 
			disYaw = disYaw - math.pi*2
		disYaw = abs( disYaw )
		if  0 <= disYaw <= off_A or  math.pi - off_A <= disYaw <= math.pi + off_A: #����
			dis =  s1 / abs( math.cos( disYaw ) )
		else: #����
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
