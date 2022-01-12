# -*- coding: utf-8 -*-

#玩家飞行管理 按照配置路径进行曲线运动 edit by wuxo 2012-2-29

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
		self.isFlyState = False  #是否开始飞翔
		self.posDatas  = []	#移动位置、时间等相关信息
		self.eventInfo = []	#事件信息
		self.isLoop    = 0      #从第几个点开始循环0为不循环
		self.maxTime   = 0	#一次运行总时间(用于循环)
		self.cbIDs     = []      #移动回调句柄
		self.eventsCB  = []      #事件回调句柄
		self.data      = None 	  #用来控制在作出选择的路线前先飞完此次节点
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
		从配置中获取位置等信息
		"""
		data = ResMgr.openSection(path)
		posDatas = []
		eventInfo = []
		if data is not None:
			for v in data.values():
				pos0 = v.readVector3("firstPos")	#一段路径的起始点
				pos1 = v.readVector3("controlPos1")	#控制点1
				pos2 = v.readVector3("controlPos2")	#控制点2
				pos3 = v.readVector3("endPos")		#一段路径的结束点（可能是另一段路径的起始点）
				startTime = v.readFloat("startTime")	#起始时间
				endTime = v.readFloat("endTime")	#结束时间
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
		posCount从初始点开始数第几个点，第一个点为0
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
		重置一些参数
		"""
		self.totalTime = 0	#运行时间
		self.lastTime  = 0      #上一次的时间
		
		
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
			self.refreshPosData(posCount)	#决定从哪个点开始飞行
		self.resetFlyData()
		self.isLoop = isLoop
		
		#改变朝向
		dPos = self.posDatas[0][0]
		p = BigWorld.player()
		matrix = Math.Matrix()
		matrix.setTranslate( dPos )
		p.turnaround( matrix)
		#首先由当前位置移动到飞行路径的第一个点
		self.gotoFisrtPos( dPos )
		#由于现在加载模型完毕后才开始飞行 于是延时回调可去掉
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
		移动回调
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
			if self.isLoop and data == self.posDatas[-1]:	#如果循环
				self.stopFly()
				if self.isLoop > 1:
					self.refreshPosData(self.isLoop)
				self.isLoop = 1
				self.resetFlyData()
				#改变朝向
				dPos = self.posDatas[0][0]
				p = BigWorld.player()
				matrix = Math.Matrix()
				matrix.setTranslate( dPos )
				p.turnaround( matrix)
				#首先由当前位置移动到飞行路径的第一个点
				functor = Functor( self.gotoFisrtPos, dPos )
				cbid = BigWorld.callback( 0.5, functor )
				self.cbIDs.append(cbid)
			else:	#播放结束
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
		播放技能
		"""
		#如果是事件ID就播放事件
		if CameraEventMgr.createEvent( skillID ):
			rds.cameraEventMgr.trigger( skillID )
		else:
			BigWorld.player().cell.requestPlaySkill( skillID )
		
		
	def stopFly(self,isCancel=True):
		"""
		停止飞行
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
		多条路径中选择离自己近的一条
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
		disData = []	#保存每条路径的第一个点离玩家的距离
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
		取消所有的回调
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