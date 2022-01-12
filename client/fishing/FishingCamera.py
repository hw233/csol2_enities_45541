# -*- coding:gb18030 -*-

import Math
import BigWorld
from gbref import rds
from CamerasMgr import FishingCameraHandler

class FishingCamera:

	def __init__( self ):
		self._cameraHandler = FishingCameraHandler()
		self._prevCamera = None

	def init( self, target, ypr, pivotDist ):
		"""初始化相机"""
		self._cameraHandler.locate(target, ypr, pivotDist)

	def setTarget( self, target ):
		"""设置相机的目标"""
		cam = self._cameraHandler.cameraShell.camera
		cam.target = target

	def setYPR( self, ypr ):
		"""设置相机的YPR(yaw, pitch, roll)"""
		camShell = self._cameraHandler.cameraShell
		camShell.setYaw( ypr[0] )
		camShell.setPitch( ypr[1] )
		camShell.camera.source.setRotateYPR( ypr )

	def setPivotDistance( self, pivotDist ):
		"""设置相机距离目标的距离"""
		camShell = self._cameraHandler.cameraShell
		camShell.setDistance(pivotDist, True)

	def use( self ):
		"""应用相机"""
		if self._prevCamera is None:
			self._prevCamera = rds.worldCamHandler
		self._cameraHandler.use()
		rds.worldCamHandler = self._cameraHandler

	def recoverToPreviousCamera( self ):
		"""恢复到先前的相机"""
		if self._prevCamera is not None:
			self._prevCamera.use()
			rds.worldCamHandler = self._prevCamera
			self._prevCamera = None

	def lockToPlayer( self ):
		"""相机锁住玩家，跟随玩家移动"""
		self.lockToEntity(BigWorld.player())

	def lockToEntity( self, entity ):
		"""相机锁住entity，跟随entity移动"""
		camShell = self._cameraHandler.cameraShell
		camShell.setEntityTarget(entity)

	def stay( self ):
		"""相机停留在当前位置"""
		cam = self._cameraHandler.cameraShell.camera
		cam.target = Math.Matrix(cam.target)
