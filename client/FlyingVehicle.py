# -*- coding: gb18030 -*-
import Role # 不要直接导入全局名字空间，否则有极大可能产生交叉引用问题
import BigWorld
import csdefine
import csconst
import Const
import Math
from RoleComponent import RoleComponent
from bwdebug import *
from VehicleHelper import isFlying

"""
Role组件
飞行骑宠相关模块

by mushuang
"""

class FlyingVehicle( RoleComponent ):
	def __init__( self, role ):
		RoleComponent.__init__( self, role )
		self.__orgBoudingBoxDepth = 0
		self.__isDeathDepthReached = False

	def isOnSomething( self ):
		"""
		检测在掉落中是否落到某物体上的算法
		目前只采取了基于垂直射线的简单碰撞检测，如果有更进一步需要，请完善此算法。 by mushuang
		"""
		srcPos = self.role.position
		dstPos = self.role.position - ( 0, Const.COLLITION_DETECTION_LEN, 0 )
		state = BigWorld.collide( self.role.spaceID, srcPos, dstPos )

		return state != None


	def enableFlyingRelatedDetection( self, spBoundingBoxMin, spBoundingBoxMax ):
		"""
		defined method
		@enableFlyingRelatedDetection: 开启和飞行有关的检测
		@spBoundingBoxMin: 空间外接盒的一个对角顶点
		@spBoundingBoxMax: 和spBoundingBoxMin相对的另一个对角顶点
		"""

		assert len( spBoundingBoxMin ) == 3, "Incorrect format for param: spBoundingBoxMin"
		assert len( spBoundingBoxMax ) == 3, "Incorrect format for param: spBoundingBoxMax"

		phy = self.role.getPhysics()
		if phy is None : return
		self.__orgBoudingBoxDepth = spBoundingBoxMin.y					# 记录下天空盒子最低深度的原始值
		# 开启场景边界碰撞
		phy.spaceBoundingBox( spBoundingBoxMin, spBoundingBoxMax )
		phy.setSpaceBoundingBoxClipCallBackFn( self.__onSpaceBoundingBoxReachedCallBack )
		phy.useSpaceBoundingBox = True
		self.updateSpaceBoundingBox()
		INFO_MSG( "Flying related detection enabled!" )

	def disableFlyingRelatedDetection( self ):
		"""
		defined method
		@disableFlyingRelatedDetection: 关闭和飞行有关的检测
		"""
		phy = self.role.getPhysics()
		if phy is None : return
		# 关闭场景边界碰撞
		phy.useSpaceBoundingBox = False
		phy.spaceBoundingBox( ( 0, 0, 0 ), ( 0, 0, 0 ) )
		phy.setSpaceBoundingBoxClipCallBackFn( None )

		INFO_MSG( "Flying related detection disabled!" )

	def updateSpaceBoundingBox( self ) :
		"""
		更新天空盒子，目前有两种情况：
		1、飞行状态下不允许超越天空盒子
		2、非飞行状态下允许穿越天空盒子底部，以便达到死亡深度，
		   触发死亡通知。
		为了实现第2种情况，在玩家处于非飞行状态时，将天空盒子的
		底部设置为一个相当低的深度，当玩家进入飞行状态时再恢复
		天空盒子的原始深度。
		"""
		phy = self.role.getPhysics()
		if phy is None : return
		if not phy.useSpaceBoundingBox : return							# 未开启天空盒子碰撞检测
		boundingBox = phy.spaceBoundingBox()
		if isFlying( self.role ) :
			boundingBox[0].y = self.__orgBoudingBoxDepth
		else :
			boundingBox[0].y = Const.SPACE_INFINITE_DEPTH				# 设置为一个非常大的深度值
		phy.spaceBoundingBox( boundingBox[0], boundingBox[1] )

	def __onSpaceBoundingBoxReachedCallBack( self ):
		"""
		在空间开启边界碰撞的情况下，玩家碰到空间的外接盒之后的回调通知
		"""
		# 注：	这里不用去修正玩家的位置，在空间开启边界碰撞的情况下，玩家会被自动推回空间内部
		# 		这个函数的存在只是为了得到相关通知。 by mushuang

		DEBUG_MSG( "Space edge reached!" )

	# ----------------------------------------------------------------------
	# 地图死亡深度检测
	# ----------------------------------------------------------------------
	def turnonDeathDepthDetect( self ) :
		"""
		开启死亡深度侦测
		"""
		self.updateDeathDepth()
		self.role.physics.setMinHeightDetectCallBackFn( self.__onMinHeightDetectedCallBack )

	def updateDeathDepth( self ) :
		"""
		更新当前地图的死亡深度
		"""
		deathDepth = float( BigWorld.getSpaceDataFirstForKey( self.role.spaceID, \
			csconst.SPACE_SPACEDATA_DEATH_DEPTH ) )
		self.role.physics.minHeightDetect = deathDepth

	def __onMinHeightDetectedCallBack( self ):
		"""
		玩家跌落到最低深度后的回调
		"""
		INFO_MSG( "Death depth reached!" )
		self.__isDeathDepthReached = True
		self.role.physics.fall = False 				# 策划要求到达死亡深度之后立即停止掉落
		self.role.cell.onMinHeightDetected()

	def isDeathDepthReached( self ) :
		"""
		是否达到了死亡深度
		"""
		return self.__isDeathDepthReached

	def resetDeathDepthReached( self ) :
		"""
		重置是否达到死亡深度的标记
		"""
		self.__isDeathDepthReached = False

	def refreshFlyingSetting( self ) :
		"""
		刷新当前控件的飞行设置
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
