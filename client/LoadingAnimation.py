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
	��ͼ����loading����
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
		���entity
		"""
		for entity in BigWorld.entities.values() :
			if entity.spaceID == self.__loginSpaceID and entity.__class__.__name__ == "CameraEntity":
				self.entity = entity
				return
		self.cbid = BigWorld.callback( 0.1, self.getEntity )
	
	def loadSpace( self ):
		"""
		���ض�������ĵ�ͼ����Ҫ��ǰ����
		"""
		if not self.__loginSpaceID:
			self.__loginSpaceID = BigWorld.createSpace()	# ��������
			BigWorld.addSpaceGeometryMapping( self.__loginSpaceID, None, LOADING_MAP )	# ���س�������
			BigWorld.worldDrawEnabled( True ) # ������������
		self.isPlay = True
	
	def startLoadingAnimation( self ):
		"""
		��ʼ����loading����
		"""
		BigWorld.cameraSpaceID( self.__loginSpaceID )	
		BigWorld.spaceHold( True )
		#pos = CAMERA_POSITION
		#dir = CAMERA_DIRECTION
		cc = rds.worldCamHandler.cameraShell.camera
		BigWorld.camera( cc )
		cc.spaceID = self.__loginSpaceID
		#m = Math.Matrix()
		#m.setTranslate( pos )	# ���㵽 space ������� chunk ��������
		#cc.target = m			# ʹ�ó�������ʱ������ּ���λ�ò���
		#cc.source.setRotateYPR( dir )
		BigWorld.callback( 20.0, self.reset )
		if self.entity:
			self.entity.usePlayerModel()
		else:
			self.getEntity()
		rds.worldCamHandler.cameraShell.camera.target = self.entity.matrix	
	
	def reset( self ):
		"""
		������ɻ�ԭ��������ͷ
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