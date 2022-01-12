# -*- coding: gb18030 -*-

#��������й��� ��������·�����������˶� edit by wuxo 2012-3-28

from bwdebug import *
import BigWorld
import Math
import time
import copy
import math
import ResMgr
import Define
import CamerasMgr
import CameraEventMgr
import csarithmetic
import SkillTargetObjImpl
from gbref import rds
from Function import Functor
import event.EventCenter as ECenter
from guis.ScreenViewer import ScreenViewer


class CameraFlyMgr:
	__instance = None

	def __init__( self ):
		assert CameraFlyMgr.__instance is None
		self.isFlyState = False  #�Ƿ�ʼ����
		self.posDatas  = []	#�ƶ�λ�á�ʱ��������Ϣ
		self.eventInfo = []	#�¼���Ϣ
		
		self.maxTime   = 0	#һ��������ʱ��(����ѭ��)
		self.cbIDs	 = []	  #�ص����
		self.status	= -1 #����״̬ -1 û������ 0 ��ͣ�� 1 ������
		self.confpath  = "" #���������ļ�
		self.isDebug   =  False
		
		self.resetFlyData()
		self.callback  = None
		self.camera = CamerasMgr.FlyCameraShell()
		self.camera.camera.positionAcceleration = 0.0
		self.camera.camera.trackingAcceleration = 0.0

	@classmethod
	def instance( self ):
		if self.__instance is None:
			self.__instance = CameraFlyMgr()
		return self.__instance
		
	def getDataFromXml(self, path):
		"""
		�������л�ȡλ�õ���Ϣ
		"""
		data = ResMgr.openSection(path)
		posDatas = []
		eventInfo = []
		if data is not None:
			for v in data.values():
				pos0 = v.readVector3("firstPos")	#һ��·������ʼ��
				pos1 = v.readVector3("controlPos1")	#���Ƶ�1
				pos2 = v.readVector3("controlPos2")	#���Ƶ�2
				pos3 = v.readVector3("endPos")		#һ��·���Ľ����㣨��������һ��·������ʼ�㣩
				startTime = v.readFloat("startTime")	#��ʼʱ��
				endTime   = v.readFloat("endTime")	#����ʱ��
				startDir = v.readVector3("firstRotate")	#��ʼ����
				endDir   = v.readVector3("endRotate")	#��������
				startRunTime   = v.readFloat("startRunTime",startTime)	#����ʱ��
				if endTime > self.maxTime:
					self.maxTime = endTime
				posDatas.append([pos0, pos1, pos2, pos3, startTime, endTime, startDir, endDir, startRunTime ])
				for k1,v1 in v.items():
					if k1 == "events":
						eventTime = v1.readFloat("startTime")
						param = v1.readString("param").split(";")
						params = [ int(i) for i in param ]
						eventInfo.append( [eventTime, params, 0] ) 
		return (posDatas,eventInfo)
			
		
		
	def resetFlyData(self):
		"""
		����һЩ����
		"""
		self.totalTime = 0	#����ʱ��
		self.lastTime  = 0      #��һ�ε�ʱ��
		
	def reloadEventPath(self, eventIDs):
		strEventIDL = eventIDs.split(";")
		eventIDL = [eval(i) for i in strEventIDL]
		for eventID in eventIDL:
			path = CameraEventMgr.createEvent( eventID ).graphID
			ResMgr.purge(path)
		
	def startCameraFly(self, path, callback = None ):
		self.confpath  = path
		self.isFlyState = True
		self.callback  = callback
		info = self.getDataFromXml(path)
		self.posDatas = info[0]
		if len( self.posDatas ) == 0: #����·�����ݴ���
			self.stopFly()
			ERROR_MSG( "------>>>CameraFlyMgr path error.%s"%path )
			return
		self.eventInfo = info[1]
		self.playCameraFly()

	def playCameraFly(self):
		self.isFlyState = True
		self.resetFlyData()
		self.status = 1
		#�ı䳯��
		dPos = self.posDatas[0][0]
		
		self.camera.reset()
		self.camera.camera.positionAcceleration = 0.0
		self.camera.camera.trackingAcceleration = 0.0
		ma = Math.Matrix()
		ma.setTranslate(dPos)
		self.camera.setMatrixTarget(ma)
		
		self.camera.setYaw( self.posDatas[0][6][0], True )
		self.camera.setPitch( math.pi - self.posDatas[0][6][1], True )
		
		BigWorld.camera( self.camera.camera )
		BigWorld.callback( 0.1, self.gotoFisrtPos )	
		
	def gotoFisrtPos(self):
		if not self.isDebug:
			for i in self.eventInfo:
				if i[0] >= 0:
					functor = Functor( self.playEvent, i[1] )
					cbid = BigWorld.callback( i[0], functor )
					self.cbIDs.append(cbid)
		self.camera.camera.positionAcceleration = 1.0 #λ������һ������ʱ��
		self.camera.camera.trackingAcceleration = 1.0 #ת������һ������ʱ��
		self.cameraFly( )	
		
	def cameraFly(self):
		if self.lastTime == 0:
			self.lastTime = time.time()
			self.cameraFly()
			return
		nowTime = time.time()
		dTime = nowTime - self.lastTime
		self.lastTime = nowTime
		
		if self.status == 0:
			cbID = BigWorld.callback( 0.0001, self.cameraFly )
			self.cbIDs.append(cbID)
			return
		self.totalTime += dTime
		
		self.fly()

	def fly(self):
		data = self.getData( self.totalTime )
		if data is None :
			if self.totalTime >= self.posDatas[-1][5]:
				self.stopFly()
			return
		pos0 = data[0] 
		pos1 = data[1] 
		pos2 = data[2]
		pos3 = data[3] 
		startTime = data[4]
		endTime = data[5]
		startRunTime  = data[8]
		
		if  startTime != startRunTime and self.totalTime < startRunTime:
			pass  #ֹͣʱ��
		else:
			data2 = self.getData( endTime + 0.01 )
			t = ( self.totalTime - startRunTime)/( endTime - startRunTime )
			t1 = 1.0 - t
			t2 = t * t
			t3 = t * t2
			
			pos = pos0 * t1**3 + 3 * pos1 * t * t1**2 + 3 * pos2 * t2 * t1 + pos3 * t3;
			
			
			ma = Math.Matrix()
			ma.setTranslate(pos)
			self.camera.setMatrixTarget(ma)
			if data2 :
				if math.fabs( data2[6][0] - data[6][0] ) > math.pi:
					if data[6][0] < 0:
						data[6][0] += 2*math.pi
					if data2[6][0] < 0:
						data[6][0] -= 2*math.pi
				yaw = data[6][0] + t * ( data2[6][0] - data[6][0] )
				pitch = math.pi - data[6][1] + t * (  - data2[6][1] + data[6][1] )
			else:
				yaw = self.posDatas[-1][6][0]
				pitch = math.pi - self.posDatas[-1][6][1]
			self.camera.setYaw( yaw, True )
			self.camera.setPitch( pitch, True )
	
		
		if self.isDebug:
			for i in self.eventInfo:
				if i[0] <= 0:
					continue
				if self.totalTime > i[0]:
					if i[2] == 0:
						print "playEvent...:", i[1]
						self.playEvent(i[1])
						i[2] = 1
				else:
					i[2] = 0
		cbID = BigWorld.callback( 0.0001, self.cameraFly )
		self.cbIDs.append(cbID)
		
	def playEvent(self, param):
		"""
		�����¼�
		"""
		#�˴�����rds.cameraEventMgr.trigger��ԭ���ǵ�ǰ�Ѿ����ھ�ͷ����״̬
		for id in param:
			CameraEventMgr.createEvent( id ).trigger()
		
		
	def stopFly(self):
		"""
		ֹͣ����
		"""
		if self.cbIDs :
			self.cancelAllCallback()
		if callable(self.callback):
			self.callback()
		self.isFlyState = False
		if BigWorld.player().__class__.__name__ == "PlayerRole":
			screenViewer = ScreenViewer()
			isHide = screenViewer.getHideByShortCut()
			if not isHide:
				ECenter.fireEvent( "EVT_ON_VISIBLE_ROOTUIS", 1 )

		self.status = -1
		
	def cancelAllCallback(self):
		"""
		ȡ�����еĻص�
		"""
		for i in self.cbIDs:
			BigWorld.cancelCallback(i)
		self.cbIDs = []
		
	def getData( self, dTime ):
		for data in self.posDatas:
			startTime = data[4]
			endTime = data[5]
			if dTime >= startTime and dTime < endTime:
				return data
		return None	

	def pauseFly(self):
		self.status = 0

	def continueFly(self):
		self.status = 1

	def setFlyTime(self, totalTime):
		self.totalTime  = totalTime

	def setTotalTime(self, totalTime):
		self.totalTime = totalTime
		self.fly()

