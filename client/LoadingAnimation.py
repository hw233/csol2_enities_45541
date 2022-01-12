# -*- coding: gb18030 -*-
#edit by wuxo 2014-4-14

import math
import Math
import Const
import Define
import BigWorld
import csdefine
import random
from gbref import rds
from Function import Functor

LOADING_MAP = "universes/fu_ben_zu_dui_jing_ji_chang"
CAMERA_POSITION  = ( 28.125,171.065,-121.424 )
CAMERA_DIRECTION = ( -178.372 * math.pi / 180,   2.864 * math.pi / 180, math.pi )


class LoadingAnimation:
	"""
	地图传送loading动画
	"""
	__inst = None

	def __init__( self ) :
		assert LoadingAnimation.__inst is None
		self.__loginSpaceID = 0
		self.isPlay = False
		self.entity = None
		self.cbid = 0
		self.actionName = "float_run"
	
	@classmethod
	def instance( SELF ) :
		if SELF.__inst is None :
			SELF.__inst = LoadingAnimation()
		return SELF.__inst
	
	def getEntity( self ):
		"""
		获得entity
		"""
		for entity in BigWorld.entities.values() :
			if entity.spaceID == self.__loginSpaceID and entity.__class__.__name__ == "CameraEntity":
				self.entity = entity
				return
		self.cbid = BigWorld.callback( 0.1, self.getEntity )
	
	def loadSpace( self ):
		"""
		加载动画所需的地图，需要提前加载
		"""
		if not self.__loginSpaceID:
			self.__loginSpaceID = BigWorld.createSpace()	# 创建场景
			BigWorld.addSpaceGeometryMapping( self.__loginSpaceID, None, LOADING_MAP )	# 加载场景数据
			BigWorld.worldDrawEnabled( True ) # 开启场景绘制
		self.isPlay = True
	
	def startLoadingAnimation( self ):
		"""
		开始播放loading动画
		"""
		BigWorld.cameraSpaceID( self.__loginSpaceID )	
		BigWorld.spaceHold( True )
		#pos = CAMERA_POSITION
		#dir = CAMERA_DIRECTION
		cc = rds.worldCamHandler.cameraShell.camera
		BigWorld.camera( cc )
		cc.spaceID = self.__loginSpaceID
		#m = Math.Matrix()
		#m.setTranslate( pos )	# 定点到 space 里面存在 chunk 的坐标上
		#cc.target = m			# 使得场景加载时不会出现加载位置不对
		#cc.source.setRotateYPR( dir )
		BigWorld.callback( 20.0, self.reset )
		if self.entity:
			self.entity.usePlayerModel()
		else:
			self.getEntity()
		rds.worldCamHandler.cameraShell.camera.target = self.entity.matrix	
	
	def reset( self ):
		"""
		加载完成还原场景、镜头
		"""
		self.isPlay = False
		self.actionName = "float_run"
		cc = rds.worldCamHandler.cameraShell.camera
		id = BigWorld.player().spaceID
		BigWorld.cameraSpaceID( id )	
		cc.spaceID = 0
		cc.target = BigWorld.player().matrix	

	def getSpaceID( self ):
		return self.__loginSpaceID

loadingAnimation = LoadingAnimation.instance()