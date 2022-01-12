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
		"""��ʼ�����"""
		self._cameraHandler.locate(target, ypr, pivotDist)

	def setTarget( self, target ):
		"""���������Ŀ��"""
		cam = self._cameraHandler.cameraShell.camera
		cam.target = target

	def setYPR( self, ypr ):
		"""���������YPR(yaw, pitch, roll)"""
		camShell = self._cameraHandler.cameraShell
		camShell.setYaw( ypr[0] )
		camShell.setPitch( ypr[1] )
		camShell.camera.source.setRotateYPR( ypr )

	def setPivotDistance( self, pivotDist ):
		"""�����������Ŀ��ľ���"""
		camShell = self._cameraHandler.cameraShell
		camShell.setDistance(pivotDist, True)

	def use( self ):
		"""Ӧ�����"""
		if self._prevCamera is None:
			self._prevCamera = rds.worldCamHandler
		self._cameraHandler.use()
		rds.worldCamHandler = self._cameraHandler

	def recoverToPreviousCamera( self ):
		"""�ָ�����ǰ�����"""
		if self._prevCamera is not None:
			self._prevCamera.use()
			rds.worldCamHandler = self._prevCamera
			self._prevCamera = None

	def lockToPlayer( self ):
		"""�����ס��ң���������ƶ�"""
		self.lockToEntity(BigWorld.player())

	def lockToEntity( self, entity ):
		"""�����סentity������entity�ƶ�"""
		camShell = self._cameraHandler.cameraShell
		camShell.setEntityTarget(entity)

	def stay( self ):
		"""���ͣ���ڵ�ǰλ��"""
		cam = self._cameraHandler.cameraShell.camera
		cam.target = Math.Matrix(cam.target)
