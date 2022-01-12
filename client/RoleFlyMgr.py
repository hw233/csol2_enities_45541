# -*- coding: utf-8 -*-

#��ҷ��й��� ��������·�����������˶� edit by wuxo 2012-2-29

from bwdebug import *
import BigWorld
import Math
import time
import copy
import ResMgr
import SkillTargetObjImpl
import CameraEventMgr
from Function import Functor
from gbref import rds

class RoleFlyMgr:
	__instance = None

	def __init__( self ):
		assert RoleFlyMgr.__instance is None
		self.isFlyState = False  #�Ƿ�ʼ����
		self.posDatas  = []	#�ƶ�λ�á�ʱ��������Ϣ
		self.eventInfo = []	#�¼���Ϣ
		self.isLoop    = 0      #�ӵڼ����㿪ʼѭ��0Ϊ��ѭ��
		self.maxTime   = 0	#һ��������ʱ��(����ѭ��)
		self.cbIDs     = []      #�ƶ��ص����
		self.eventsCB  = []      #�¼��ص����
		self.data      = None 	  #��������������ѡ���·��ǰ�ȷ���˴νڵ�
		self.paths     = None
		self.cb        = None
		self.resetFlyData()
		self.callback  = None
		

	@classmethod
	def instance( self ):
		if self.__instance is None:
			self.__instance = RoleFlyMgr()
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
				endTime = v.readFloat("endTime")	#����ʱ��
				if endTime > self.maxTime:
					self.maxTime = endTime
				posDatas.append([pos0, pos1, pos2, pos3, startTime, endTime])
				for k1,v1 in v.items():
					if k1 == "events":
						eventTime = v1.readFloat("startTime")
						param = v1.readInt("param")
						if param != 0:
							eventInfo.append( [eventTime, param] ) 
		return (posDatas,eventInfo)
		
	def refreshPosData( self, posCount ):
		"""
		posCount�ӳ�ʼ�㿪ʼ���ڼ����㣬��һ����Ϊ0
		"""
		self.posDatas = self.posDatas[ posCount-1 : ]
		stime = self.posDatas[0][4]
		self.maxTime -= stime
		for index in xrange(len(self.posDatas)):
			self.posDatas[index][4] -= stime
			self.posDatas[index][5] -= stime
		for idx in xrange(len(self.eventInfo)):
			self.eventInfo[idx][0] -= stime
			
		
		
	def resetFlyData(self):
		"""
		����һЩ����
		"""
		self.totalTime = 0	#����ʱ��
		self.lastTime  = 0      #��һ�ε�ʱ��
		
		
	def startRoleFly(self, path, posCount = 0, isLoop = 1,callback = None ):
		self.stopFly()
		self.data  = None
		self.paths     = None
		self.cb        = None
		self.isFlyState = True
		self.callback  = callback
		info = self.getDataFromXml(path)
		self.posDatas = info[0]
		self.eventInfo = info[1]
		if posCount - 1 > 0:
			self.refreshPosData(posCount)	#�������ĸ��㿪ʼ����
		self.resetFlyData()
		self.isLoop = isLoop
		
		#�ı䳯��
		dPos = self.posDatas[0][0]
		p = BigWorld.player()
		matrix = Math.Matrix()
		matrix.setTranslate( dPos )
		p.turnaround( matrix)
		#�����ɵ�ǰλ���ƶ�������·���ĵ�һ����
		self.gotoFisrtPos( dPos )
		#�������ڼ���ģ����Ϻ�ſ�ʼ���� ������ʱ�ص���ȥ��
		#functor = Functor( self.gotoFisrtPos, dPos )
		#if BigWorld.player().continueFlyPath != "":
		#	self.gotoFisrtPos( dPos )
		#else:
		#	cbid = BigWorld.callback( 1.5, functor )
		#	self.cbIDs.append(cbid)
		
	def gotoFisrtPos(self,dPos):
		try:
			BigWorld.player().model.action("fly")()
		except:
			ERROR_MSG( ">>>>>>>>>>>>role has no action: fly"  )
		BigWorld.player().moveToDirectly( dPos, self.__onMoveSuccess )	
		
		
	def __onMoveSuccess(self,isSucceed):
		"""
		�ƶ��ص�
		"""
		self.roleFly()
		for i in self.eventInfo:
			if i[0] >= 0:
				functor = Functor( self.playSkill, i[1] )
				cbid = BigWorld.callback( i[0], functor )
				self.eventsCB.append(cbid)
		
	def roleFly(self):
		if self.lastTime == 0:
			self.lastTime = time.time()
			self.roleFly ()
			return
		nowTime = time.time()
		dTime = nowTime - self.lastTime
		self.totalTime += dTime
		self.lastTime = nowTime
		
		data = self.getData( self.totalTime )
		if data != None and data == self.data :
			self.startCheckFly()
		if data is None or data == self.posDatas[-1]:
			if self.isLoop and data == self.posDatas[-1]:	#���ѭ��
				self.stopFly()
				if self.isLoop > 1:
					self.refreshPosData(self.isLoop)
				self.isLoop = 1
				self.resetFlyData()
				#�ı䳯��
				dPos = self.posDatas[0][0]
				p = BigWorld.player()
				matrix = Math.Matrix()
				matrix.setTranslate( dPos )
				p.turnaround( matrix)
				#�����ɵ�ǰλ���ƶ�������·���ĵ�һ����
				functor = Functor( self.gotoFisrtPos, dPos )
				cbid = BigWorld.callback( 0.5, functor )
				self.cbIDs.append(cbid)
			else:	#���Ž���
				if callable(self.callback):
					self.callback()	
			return
		pos0 = data[0] 
		pos1 = data[1] 
		pos2 = data[2]
		pos3 = data[3] 
		startTime = data[4]
		endTime = data[5]
		
		distance = pos3.distTo( pos0 )
		move_speed = distance/( endTime - startTime )
		BigWorld.player().move_speed = move_speed
		
		t = ( self.totalTime - startTime)/( endTime - startTime )
		t1 = 1.0 - t
		t2 = t * t
		t3 = t * t2
		
		pos = pos0 * t1**3 + 3 * pos1 * t * t1**2 + 3 * pos2 * t2 * t1 + pos3 * t3;
		
		BigWorld.player().moveToDirectly( pos )
		
		cbID = BigWorld.callback( 0.0001, self.roleFly )
		self.cbIDs.append(cbID)
		
	def playSkill(self, skillID):
		"""
		���ż���
		"""
		#������¼�ID�Ͳ����¼�
		if CameraEventMgr.createEvent( skillID ):
			rds.cameraEventMgr.trigger( skillID )
		else:
			BigWorld.player().cell.requestPlaySkill( skillID )
		
		
	def stopFly(self,isCancel=True):
		"""
		ֹͣ����
		"""
		self.cancelAllCallback()
		if isCancel :
			for i in self.eventsCB:
				BigWorld.cancelCallback(i)
			self.eventsCB = []	
		BigWorld.player().stopMove( )
		self.isFlyState = False

	def doCheckFly(self, paths, callback = None):
		"""
		����·����ѡ�����Լ�����һ��
		"""
		data  = self.getData( self.totalTime )
		if data and self.posDatas and self.posDatas.index(data) < len(self.posDatas) -1 :
			idx = self.posDatas.index(data)
			self.data = self.posDatas[ idx + 1 ]
		else:	
			self.startCheckFly()
		self.paths = paths
		self.cb = callback
		
	def startCheckFly(self):	
		self.stopFly()
		disData = []	#����ÿ��·���ĵ�һ��������ҵľ���
		pos = BigWorld.player().position
		for path in self.paths:
			info = self.getDataFromXml(path)
			dis = (pos - info[0][0][0]).length
			disData.append(dis)
		disData_copy = copy.deepcopy( disData )
		disData.sort()
		idx = disData_copy.index( disData[0] )
		self.startRoleFly( self.paths[idx], 0 , 0 , self.cb )
		
		
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