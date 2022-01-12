# -*- coding: gb18030 -*-
import Role # ��Ҫֱ�ӵ���ȫ�����ֿռ䣬�����м�����ܲ���������������
import BigWorld
import csdefine
import csconst
import Const
import Math
from RoleComponent import RoleComponent
from bwdebug import *
from VehicleHelper import isFlying

"""
Role���
����������ģ��

by mushuang
"""

class FlyingVehicle( RoleComponent ):
	def __init__( self, role ):
		RoleComponent.__init__( self, role )
		self.__orgBoudingBoxDepth = 0
		self.__isDeathDepthReached = False

	def isOnSomething( self ):
		"""
		����ڵ������Ƿ��䵽ĳ�����ϵ��㷨
		Ŀǰֻ��ȡ�˻��ڴ�ֱ���ߵļ���ײ��⣬����и���һ����Ҫ�������ƴ��㷨�� by mushuang
		"""
		srcPos = self.role.position
		dstPos = self.role.position - ( 0, Const.COLLITION_DETECTION_LEN, 0 )
		state = BigWorld.collide( self.role.spaceID, srcPos, dstPos )

		return state != None


	def enableFlyingRelatedDetection( self, spBoundingBoxMin, spBoundingBoxMax ):
		"""
		defined method
		@enableFlyingRelatedDetection: �����ͷ����йصļ��
		@spBoundingBoxMin: �ռ���Ӻе�һ���ԽǶ���
		@spBoundingBoxMax: ��spBoundingBoxMin��Ե���һ���ԽǶ���
		"""

		assert len( spBoundingBoxMin ) == 3, "Incorrect format for param: spBoundingBoxMin"
		assert len( spBoundingBoxMax ) == 3, "Incorrect format for param: spBoundingBoxMax"

		phy = self.role.getPhysics()
		if phy is None : return
		self.__orgBoudingBoxDepth = spBoundingBoxMin.y					# ��¼����պ��������ȵ�ԭʼֵ
		# ���������߽���ײ
		phy.spaceBoundingBox( spBoundingBoxMin, spBoundingBoxMax )
		phy.setSpaceBoundingBoxClipCallBackFn( self.__onSpaceBoundingBoxReachedCallBack )
		phy.useSpaceBoundingBox = True
		self.updateSpaceBoundingBox()
		INFO_MSG( "Flying related detection enabled!" )

	def disableFlyingRelatedDetection( self ):
		"""
		defined method
		@disableFlyingRelatedDetection: �رպͷ����йصļ��
		"""
		phy = self.role.getPhysics()
		if phy is None : return
		# �رճ����߽���ײ
		phy.useSpaceBoundingBox = False
		phy.spaceBoundingBox( ( 0, 0, 0 ), ( 0, 0, 0 ) )
		phy.setSpaceBoundingBoxClipCallBackFn( None )

		INFO_MSG( "Flying related detection disabled!" )

	def updateSpaceBoundingBox( self ) :
		"""
		������պ��ӣ�Ŀǰ�����������
		1������״̬�²�����Խ��պ���
		2���Ƿ���״̬������Խ��պ��ӵײ����Ա�ﵽ������ȣ�
		   ��������֪ͨ��
		Ϊ��ʵ�ֵ�2�����������Ҵ��ڷǷ���״̬ʱ������պ��ӵ�
		�ײ�����Ϊһ���൱�͵���ȣ�����ҽ������״̬ʱ�ٻָ�
		��պ��ӵ�ԭʼ��ȡ�
		"""
		phy = self.role.getPhysics()
		if phy is None : return
		if not phy.useSpaceBoundingBox : return							# δ������պ�����ײ���
		boundingBox = phy.spaceBoundingBox()
		if isFlying( self.role ) :
			boundingBox[0].y = self.__orgBoudingBoxDepth
		else :
			boundingBox[0].y = Const.SPACE_INFINITE_DEPTH				# ����Ϊһ���ǳ�������ֵ
		phy.spaceBoundingBox( boundingBox[0], boundingBox[1] )

	def __onSpaceBoundingBoxReachedCallBack( self ):
		"""
		�ڿռ俪���߽���ײ������£���������ռ����Ӻ�֮��Ļص�֪ͨ
		"""
		# ע��	���ﲻ��ȥ������ҵ�λ�ã��ڿռ俪���߽���ײ������£���һᱻ�Զ��ƻؿռ��ڲ�
		# 		��������Ĵ���ֻ��Ϊ�˵õ����֪ͨ�� by mushuang

		DEBUG_MSG( "Space edge reached!" )

	# ----------------------------------------------------------------------
	# ��ͼ������ȼ��
	# ----------------------------------------------------------------------
	def turnonDeathDepthDetect( self ) :
		"""
		��������������
		"""
		self.updateDeathDepth()
		self.role.physics.setMinHeightDetectCallBackFn( self.__onMinHeightDetectedCallBack )

	def updateDeathDepth( self ) :
		"""
		���µ�ǰ��ͼ���������
		"""
		deathDepth = float( BigWorld.getSpaceDataFirstForKey( self.role.spaceID, \
			csconst.SPACE_SPACEDATA_DEATH_DEPTH ) )
		self.role.physics.minHeightDetect = deathDepth

	def __onMinHeightDetectedCallBack( self ):
		"""
		��ҵ��䵽�����Ⱥ�Ļص�
		"""
		INFO_MSG( "Death depth reached!" )
		self.__isDeathDepthReached = True
		self.role.physics.fall = False 				# �߻�Ҫ�󵽴��������֮������ֹͣ����
		self.role.cell.onMinHeightDetected()

	def isDeathDepthReached( self ) :
		"""
		�Ƿ�ﵽ���������
		"""
		return self.__isDeathDepthReached

	def resetDeathDepthReached( self ) :
		"""
		�����Ƿ�ﵽ������ȵı��
		"""
		self.__isDeathDepthReached = False

	def refreshFlyingSetting( self ) :
		"""
		ˢ�µ�ǰ�ؼ��ķ�������
		"""
		if not self.role.inWorld : return
		self.turnonDeathDepthDetect()
		if eval( BigWorld.getSpaceDataFirstForKey( self.role.spaceID, \
			csconst.SPACE_SPACEDATA_CAN_FLY ) ) :
				spBoundingBoxMin = Math.Vector3( eval( BigWorld.getSpaceDataFirstForKey( self.role.spaceID, \
					csconst.SPACE_SPACEDATA_MIN_BBOX ) ) )
				spBoundingBoxMax = Math.Vector3( eval( BigWorld.getSpaceDataFirstForKey( self.role.spaceID, \
					csconst.SPACE_SPACEDATA_MAX_BBOX ) ) )
				self.enableFlyingRelatedDetection( spBoundingBoxMin, spBoundingBoxMax )
		else :
			self.disableFlyingRelatedDetection()
