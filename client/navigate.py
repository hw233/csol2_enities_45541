# -*- coding: gb18030 -*-
#2009-7-11  writen by QIULINHUI
import BigWorld
import Math
import math
from bwdebug import *
import random
import csol
import time
from Function import Functor
from SpaceDoorMgr import SpaceDoorMgr
import weakref


class NavigateEx:
	#"常量"定义
	IGNORE_LEN 		= 0.5
	IGNORE_ANGLE 	= math.pi / 4
	INVALIDITY_POS	= Math.Vector3( -100000000, -100000000, -100000000 ) #标志为无效的值
	#状态定义,注意这些状态不会共存
	NAV_STATE_NONE			= 0				#空状态
	NAV_STATE_PURSUE		= 1				#跟踪状态
	NAV_STATE_MCTRL			= 2				#mouseCtrlRun
	NAV_STATE_SDEST			= 3				#triggerRun同一场景寻路
	NAV_STATE_LDEST			= 4				#triggerRun跨场景寻路
	NAV_STATE_TRAP 			= 5				#寻路卡位:开始时便陷入困境,不能自拔
	def __init__( self, owner ):
		self.__owner = weakref.proxy( owner, self.__onOwnerLost )
		self.__navExPath = [] #实际的路径
		self.__perfectPath = [] #给界面显示的路径
		self.__navExPathIndex = 0
		self.__navExReachGoalFunctor = None
		self.__nearbyCheckEventID = 0
		self.__purseEventID = 0
		self.__purseCheckCount = 0
		self.__pursueTarget = None
		self.__pauseNearby = 0
		self.__pauseCallback = None
		self.__spaceDoorPath = []
		self.__spaceGoalPos = Math.Vector3( NavigateEx.INVALIDITY_POS )
		self.__spaceNearBy = 0
		self.__curNearBy = 0
		self.__trapCount	= 0
		self.__startPos		= Math.Vector3( NavigateEx.INVALIDITY_POS )
		self.__prePos		= Math.Vector3( NavigateEx.INVALIDITY_POS )
		self.__resumeNavigateCount = 0
		self.__resumeNavigateLock = False
		self.__trapDetectEventID = 0
		self.__onEnterNavState( NavigateEx.NAV_STATE_NONE )

	def __onOwnerLost( self, proxy ):
		"""owner被销毁了"""
		self.__stop()
		if self.needContinueLongSearch():
			self.clearSpaceDoorPath()

	def __onCollisionCBF( self ):
		"""
		自动寻路状态中，碰到障碍物而无法走到的回调函数
		"""
		self.__onGoalReach( False )

	def __onEnterNavState( self, navState ):
		"""
		进入某种状态时,触发此函数
		@type		navState: NAV_STATE TYPE
		@param		navState: NAV_STATE
		"""
		self.__navExState = navState

	def __findDropPoint( self, point ):
		"""
		拾取地面处理
		@type		point: Vector3
		@param		point: 有待拾取地面的点
		"""
		testPos = Math.Vector3( point )
		testPos.y += 3
		dp = BigWorld.findDropPoint( self.__owner.spaceID, testPos )
		if dp is not None:
			testPos.y = dp[0].y
		else:
			testPos.y = point.y
		return testPos

	def __trapDetect( self ):
		"""
		由于场景原因，卡位无法移动的侦测
		"""
		self.__cancelTrapDetect()
		TRAP_TOLERANCE_SQ_LEN	= 0.0001
		curPos = self.__owner.position
		self.__trapCount   = curPos.distSqrTo( self.__prePos ) < TRAP_TOLERANCE_SQ_LEN \
							 and self.__trapCount + 1 or 0
		if self.__trapCount > 1 and self.__resumeNavigateCount < 3:
			self.__resumeNavigateCount += 1
			self.__resumeNavigateLock = True
			BigWorld.player().resumeAutoRun()
			self.__resumeNavigateLock = False
			return
		if self.__trapCount >= 5:
			self.__trapDetectEventID = 0
			self.__owner.onNavigateExNoPathFind( NavigateEx.NAV_STATE_TRAP )
			self.__onCollisionCBF()
			return
		self.__prePos = Math.Vector3( curPos )
		self.__trapDetectEventID = BigWorld.callback( 0.3, self.__trapDetect )

	def __cancelTrapDetect( self ):
		"""
		取消trapDetect事件
		"""
		if self.__trapDetectEventID != 0:
			BigWorld.cancelCallback( self.__trapDetectEventID )
			self.__trapDetectEventID = 0

	def __onGoalReach( self, isSuccess ):
		"""
		抵达目的点时的回调函数
		@type		isSuccess: bool/int
		@param		isSuccess:
		"""
		self.__cancelTrapDetect()
		self.__navExPathIndex = 0
		if self.needContinueLongSearch():
			return
		if self.__navExReachGoalFunctor is not None:
			fn = self.__navExReachGoalFunctor
			self.__navExReachGoalFunctor = None
			fn( isSuccess )

	def __navExGo( self, isSuccess ):
		"""
		@type		isSuccess: bool/int
		@param		isSuccess:
		"""
		if isSuccess:
			self.__trapCount = 0
		self.__navExPathIndex += 1
		pathLen = len( self.__navExPath )
		if self.__navExPathIndex < pathLen - 1: #路漫漫其修远兮
			callback = self.__navExGo
			isSeekToGoal = False
		elif self.__navExPathIndex == pathLen - 1: #冲锋在即
			callback = self.__onGoalReach
			isSeekToGoal = True
			self.__cancelTrapDetect()
			self.__owner.getPhysics().setSeekCollisionCallBackFn( self.__onCollisionCBF )
		else: #抵达目的点时
			self.__onGoalReach( True )
			return
		dstPos = self.__findDropPoint( self.__navExPath[self.__navExPathIndex] )
		self.__owner.seek( dstPos, 1000, callback, isSeekToGoal )

	def __stop( self ):
		"""
		停止寻路事件
		"""
		if not self.__resumeNavigateLock:
			self.__resumeNavigateCount = 0
		self.__trapCount   = 0
		try:
			physics = self.__owner.getPhysics()
			if physics:
				physics.setSeekCollisionCallBackFn( None )
				if physics.seeking:
					physics.setSeekCallBackFn( None )
					physics.seek( None, 0, 0, None )
		except:
			pass
		if self.__navExPathIndex != 0:
			self.__navExPathIndex = 0
			self.__onGoalReach( False )
		self.__perfectPath = []
		self.__navExPath = []
		self.__purseCheckCount = 0
		self.__pursueTarget = None
		self.__pauseNearby = 0
		self.__pauseCallback = None
		self.__curNearBy = 0
		self.__onEnterNavState( NavigateEx.NAV_STATE_NONE )
		self.__navExReachGoalFunctor = None
		if self.__nearbyCheckEventID != 0:
			BigWorld.cancelCallback( self.__nearbyCheckEventID )
			self.__nearbyCheckEventID = 0
		if self.__purseEventID != 0:
			BigWorld.cancelCallback( self.__purseEventID )
			self.__purseEventID = 0
		self.__cancelTrapDetect()

	def __setNearBy( self, nearby, dstSpaceLabel ):
		"""
		设置寻路到目标点附近的侦测距离
		@type		nearby:        float
		@param		nearby:        移动到目标位置附近的距离
		@type		dstSpaceLabel: string
		@param		dstSpaceLabel: 目标Space Name
		"""
		if not self.needContinueLongSearch() or dstSpaceLabel != "":
			self.__spaceNearBy = nearby

	def __getNearBy( self ):
		"""
		获取当前场景中,寻路到目标点附近的侦测距离
		"""
		if self.needContinueLongSearch():
			return 0
		else:
			return self.__spaceNearBy

	def __onNearbyCheck( self ):
		"""
		侦测回调事件
		"""
		BigWorld.cancelCallback( self.__nearbyCheckEventID )
		dst = Math.Vector3( self.__owner.position ).distTo( self.getGoalPosition() )
		if  dst < self.__curNearBy:
			self.__onGoalReach( True )
			return
		delay = dst/100
		if delay < 0.2:
			delay = 0.2
		self.__nearbyCheckEventID = BigWorld.callback( delay, self.__onNearbyCheck )

	def __nearbyCheck( self, nearby ):
		"""
		移动到目标位置附近的侦测
		@type			nearby: float
		@param			nearby: 移动到目标位置附近的距离(单位m)
		"""
		self.__curNearBy = nearby
		if self.__curNearBy > 0:
			self.__onNearbyCheck()

	def __onPursueOver( self, callback, isSuccess ):
		"""
		pursue事件中路径完成时的回调函数
		@type		callback:  Functor
		@param		callback:  回调函数
		@type		isSuccess: bool
		@param		isSuccess: 是否抵达目的点
		"""
		if callable( callback ):
			callback( isSuccess )
		self.__onPursueEvent()

	def __onPursuePosOver( self, callback, isSuccess ):
		"""
		pursue事件中路径完成时的回调函数
		@type		callback:  Functor
		@param		callback:  回调函数
		@type		isSuccess: bool
		@param		isSuccess: 是否抵达目的点
		"""
		if callable( callback ):
			callback( isSuccess )
		# 以下调用上一个版本是BigWorld.callback(0,__onPursuePosEvent)
		# 但是这个方式很容易和pursueEntity发生冲突，即：当调用了
		# BigWorld.callback(0,__onPursuePosEvent)之后，在回调触发前调
		# 用pursueEntity追踪，接着回调触发了，这时__onPursuePosEvent中
		# 回调的内容将是pursueEntity设置的内容，包括回调函数并非调用
		# pursuePosition时设置的函数，而是pursueEntity设置的函数，因此
		# 回调的内容出现了与预期不符的情况
		self.__onPursuePosEvent()

	def __onPursueEvent( self ):
		"""
		pursue回调事件
		"""
		owner = self.__owner
		callback = self.__pauseCallback
		BigWorld.cancelCallback( self.__purseEventID )
		self.__purseEventID = 0
		if self.__pursueTarget is None or not self.__pursueTarget.inWorld:
			if callback is not None:
				self.__navExPathIndex = 0
				self.__stop()
				owner.onPursueOver( False )
				BigWorld.callback( 0, Functor( callback, owner, None, False ) )
			return
		if owner.position.distTo( self.__pursueTarget.position ) <= self.__pauseNearby:
			if callback is not None:
				self.__navExPathIndex = 0
				target = self.__pursueTarget
				self.__stop()
				owner.endAutoRun( True )
				owner.onPursueOver( True )
				BigWorld.callback( 0, Functor( callback, owner, target, True) )
			return
		if not owner.isPursueState():
			return
		self.__purseCheckCount += 1
		if self.__purseCheckCount > 15:
			self.__purseCheckCount = 0
			physics = owner.getPhysics()
			if physics is None: return
			if physics.seeking:
				physics.setSeekCallBackFn( None )
				physics.seek( None, 0, 0, None )
			if not self.__autoRun( self.__pursueTarget.position, Functor( self.__onPursueOver, None ) ):
				return
		self.__purseEventID = BigWorld.callback( 0.1, self.__onPursueEvent )

	def __onPursuePosEvent( self ):
		"""
		pursue回调事件
		"""
		owner = self.__owner
		callback = self.__pauseCallback
		BigWorld.cancelCallback( self.__purseEventID )
		self.__purseEventID = 0
		if self.__pursuePos is None:
			if callback is not None:
				self.__navExPathIndex = 0
				self.__stop()
				owner.onPursueOver( False )
				BigWorld.callback( 0, Functor( callback, owner, None, False ) )
			return

		if owner.position.distTo( self.__pursuePos ) <= self.__pauseNearby:
			if callback is not None:
				self.__navExPathIndex = 0
				targetPos = self.__pursuePos
				self.__stop()
				owner.onPursueOver( True )
				BigWorld.callback( 0, Functor( callback, owner, targetPos, True) )
			return
		if not owner.isPursueState():
			return
		self.__purseCheckCount += 1
		if self.__purseCheckCount > 15:
			self.__purseCheckCount = 0
			physics = owner.getPhysics()
			if physics is None: return
			if physics.seeking:
				physics.setSeekCallBackFn( None )
				physics.seek( None, 0, 0, None )
			if not self.__autoRun( self.__pursuePos, Functor( self.__onPursuePosOver, None ) ):
				return
		self.__purseEventID = BigWorld.callback( 0.1, self.__onPursuePosEvent )

	def __getNearPosInWaypoint( self ):
		"""
		返回L米内，可以到达的且位于waypoint内的位置
		"""
		navMgr = NavDataMgr.instance()
		curPos = Math.Vector3( self.__owner.position )
		if ( not navMgr.isNavDataReady() ) or navMgr.isInWayPoint( curPos ):
			return curPos
		physics = self.__owner.getPhysics()
		anglePi = math.pi / 18.0
		if random.randint(0, 1) == 1:
			anglePi = -anglePi
		angle = self.__owner.yaw
		testSrcPos = Math.Vector3( 0, 0, 0 )
		L = 4
		HOLD_ON_TOLERANCE_SQ_LEN	= 0.1
		trapDirSet = set()
		for ln in xrange( 1, L + 1 ):
			for s in xrange( 36 ):
				if s in trapDirSet:
					continue
				sn = s*anglePi + angle
				testSrcPos.y = curPos.y
				testSrcPos.x = curPos.x + ln * math.sin( sn )
				testSrcPos.z = curPos.z + ln * math.cos( sn )
				tryPos = physics.canMoveToWithSlideWall( testSrcPos )
				if navMgr.isInWayPoint( tryPos ):
					return tryPos
				if tryPos.distSqrTo( curPos ) < HOLD_ON_TOLERANCE_SQ_LEN:
					trapDirSet.add( s )
		#default
		return curPos

	def __getSrcAndNearDstPos( self, srcPos, dstPos ):
		"""
		返回srcPos和可以抵达dstPos附近的点组成的元组(Vector3， [Vector3, ...]), 没有找到时，返回None
		@type			srcPos: Vector3
		@param			srcPos: 源点
		@type			dstPos: Vector3
		@param			dstPos: 目标点
		"""
		navMgr = NavDataMgr.instance()
		if not navMgr.isNavDataReady():
			return None
		anglePi = math.pi/4.0
		testSrcPos = Math.Vector3(0, 0, 0)
		L = 4
		for ln in xrange( 1, L + 1 ):
			for s in xrange( 8 ):
				sn = s*anglePi
				testSrcPos.y = dstPos.y + 2
				testSrcPos.x = dstPos.x + ln * math.sin( sn )
				testSrcPos.z = dstPos.z + ln * math.cos( sn )
				goalPosLst = navMgr.canNavigateTo( srcPos, testSrcPos )
				if len( goalPosLst ) > 0:
					return ( testSrcPos, goalPosLst )
		return None

	def __getBestGoalPos( self, goalPosLst, testPos ):
		"""
		获取最佳的目的点
		@type		return: Vector3
		@param		return: 最佳的目的点
		@type		goalPosLst: list of Vector3
		@param		goalPosLst: 可以到达的目的点列表
		@type		testPos: Vector3
		@param		testPos: 测试点
		"""
		gPos = self.__findDropPoint( testPos )
		minYOffset = 999999
		bestPos = gPos
		for p in goalPosLst:
			curYOffset = math.fabs( p.y - gPos.y )
			if curYOffset < minYOffset:
				minYOffset = curYOffset
				bestPos = Math.Vector3( p )
		return bestPos

	def __genAutoRunPath( self, goalPos ):
		"""
		生成当前场景,原位置到goalPos的路径
		注意:没有路径抵达goalPos时,会回调Action.onNavigateExNoPathFind接口
		@type			RETURN: bool
		@param			RETURN: 目的地是否可以抵达
		@type			goalPos: Vector3
		@param			goalPos: 目的点
		"""
		self.__perfectPath = []
		self.__navExPath = []
		self.__navExPathIndex = 0
		self.__startPos = Math.Vector3( self.__owner.position )
		self.__prePos   = Math.Vector3( NavigateEx.INVALIDITY_POS )
		navMgr = NavDataMgr.instance()
		if navMgr.isReachGoal( self.__startPos, goalPos ):
			return True
		navExPath = navMgr.tryBestFindPath(self.__startPos, goalPos, self.__owner.spaceID, True)
		if len(navExPath) < 1:
			self.__owner.onNavigateExNoPathFind( self.__navExState )
			self.forceStop()
			return False
		else:
			self.__navExPath = navExPath
			return True

	def __setGoalPosition( self, goalPos, dstSpaceLabel ):
		"""
		设置目标点
		@type		RETURN: bool
		@param		RETURN: 目的地是否可以抵达
		@type		pos: Vector3
		@param		pos: 目标点
		@type		dstSpaceLabel: string
		@param		dstSpaceLabel: 目标Space Name
		"""
		if dstSpaceLabel != "":
			srcPos = self.__owner.position
			srcSpaceLabel = BigWorld.player().getSpaceLabel()
			self.__spaceDoorPath = SpaceDoorMgr.instance().getPath( srcSpaceLabel, srcPos, dstSpaceLabel, goalPos )
			if len( self.__spaceDoorPath ) == 0:
				self.__owner.onNavigateExNoPathFind( self.__navExState )
				self.forceStop()
				return False
			self.__spaceGoalPos = self.__spaceDoorPath.pop(-1)[1]
		if not self.needContinueLongSearch():
			self.__spaceGoalPos  = Math.Vector3( goalPos )
		return True

	def __autoRun( self, goalPos, reachGoalFunctor,  nearby = 0.0,  dstSpaceLabel = "" ):
		"""
		@type			RETURN: bool
		@param			RETURN: 目的地是否可以抵达
		@type			goalPos: Vector3
		@param			goalPos: 寻路到指定的点
		@type 			reachGoalCallBack: func
		@param			reachGoalCallBack: 抵达目的点时的回调函数
		@type			nearby: float
		@param			nearby: 移动到目标位置附近的距离
		@type			dstSpaceLabel: string
		@param			dstSpaceLabel: 目标场景标签名
		"""
		if not self.__setGoalPosition( goalPos, dstSpaceLabel ):
			return False
		self.__setNearBy( nearby, dstSpaceLabel )
		if not self.__genAutoRunPath( self.getGoalPosition() ):
			return False
		self.__navExReachGoalFunctor = reachGoalFunctor
		self.__owner.getPhysics().setSeekCollisionCallBackFn( None )
		self.__navExGo( False )
		self.__nearbyCheck( self.__getNearBy() )
		if self.__navExState != NavigateEx.NAV_STATE_PURSUE and len( self.__navExPath ) > 2:
			self.__trapDetect()
		return True

	#----------------------------------public--------------------------------------------
	def mouseCtrlRun( self, goalPos, reachGoalFunctor):
		"""
		点击鼠标的移动方案
		@type			RETURN: bool
		@param			RETURN: 目的地是否可以抵达
		@type			goalPos: Vector3
		@param			goalPos: 寻路到指定的点
		@type 			reachGoalCallBack: func
		@param			reachGoalCallBack: 抵达目的点时的回调函数
		"""
		self.__onEnterNavState( NavigateEx.NAV_STATE_MCTRL )
		return self.__autoRun( goalPos, reachGoalFunctor )

	def triggerRun( self, goalPos, reachGoalFunctor,  nearby = 0.0,  dstSpaceLabel = "" ):
		"""
		其它触发事件的移动方案
		@type			RETURN: bool
		@param			RETURN: 目的地是否可以抵达
		@type			goalPos: Vector3
		@param			goalPos: 寻路到指定的点
		@type 			reachGoalCallBack: func
		@param			reachGoalCallBack: 抵达目的点时的回调函数
		@type			nearby: float
		@param			nearby: 移动到目标位置附近的距离
		@type			dstSpaceLabel: string
		@param			dstSpaceLabel: 目标场景标签名
		"""
		srcSpaceLabel = BigWorld.player().getSpaceLabel()
		if srcSpaceLabel == dstSpaceLabel:
			dstSpaceLabel = "" #目标点在当前场景，不启用跨场景搜索

		if dstSpaceLabel == "":
			self.__onEnterNavState( NavigateEx.NAV_STATE_SDEST )
		else:
			self.__onEnterNavState( NavigateEx.NAV_STATE_LDEST )
		return self.__autoRun( goalPos, reachGoalFunctor, nearby, dstSpaceLabel )

	def getNavPosLst( self ):
		"""
		过滤长度小于IGNORE_LEN的线段，用于修正采用LineGUIComponent画点时，出现点重叠的情况
		过滤夹角小于IGNORE_ANGLE的顶点, 用于修正采用LineGUIComponent画点时，出现长折线的情况
		"""
		if len( self.__perfectPath ) > 0:
			return self.__perfectPath

		if not NavDataMgr.instance().isNavDataReady():
			return []

		path = [self.__owner.position]
		path.extend( self.__navExPath )
		i = 1
		while i < len( path ) - 1:
			if path[i-1].distTo( path[i] ) < NavigateEx.IGNORE_LEN:
				path.pop( i )
			else:
				i += 1
		cosVal = math.cos( NavigateEx.IGNORE_ANGLE )
		i = 1
		while i < len( path ) - 1:
			ba = path[i-1] - path[i]
			ba.normalise()
			bc = path[i+1] - path[i]
			bc.normalise()
			if  ba.dot( bc ) > cosVal:
				path.pop( i )
			else:
				i += 1
		self.__perfectPath = path
		return self.__perfectPath

	def pursueEntity( self, target, nearby, callback ):
		"""
		跟踪一个目标
		@type			target: instance
		@param			target: entity you want to pursue
		@type			nearby: float
		@param			nearby: 到达目标位置附近多少米便停下来
		@type			callback: callback functor
		@param			callback: 完成跟踪后的回调函数
		"""
		self.__onEnterNavState( NavigateEx.NAV_STATE_PURSUE )
		self.__purseCheckCount = 888
		self.__pursueTarget = target
		self.__pauseNearby = nearby
		self.__pauseCallback = callback
		self.__onPursueEvent()

	def pursuePosition( self, pos, nearby, callback ):
		"""
		跟踪一个目标
		@type			target: instance
		@param			target: entity you want to pursue
		@type			nearby: float
		@param			nearby: 到达目标位置附近多少米便停下来
		@type			callback: callback functor
		@param			callback: 完成跟踪后的回调函数
		"""
		self.__onEnterNavState( NavigateEx.NAV_STATE_PURSUE )
		self.__purseCheckCount = 888
		self.__pursuePos = pos
		self.__pauseNearby = nearby
		self.__pauseCallback = callback
		self.__onPursuePosEvent()

	def needContinueLongSearch( self ):
		"""
		判断是否继续进行长距离寻路
		"""
		return len( self.__spaceDoorPath ) != 0

	def clearSpaceDoorPath( self ):
		"""
		清空跨场景寻路信息数据
		"""
		self.__spaceDoorPath = []

	def tryContinueLongSearch( self ):
		"""
		尝试继续长距离寻路，成功返回True，失败返回False
		"""
		if self.needContinueLongSearch() and NavDataMgr.instance().isNavDataReady():
			self.__spaceDoorPath.pop(0)
			targetPos = self.getGoalPosition()
			nearby = self.__getNearBy()
			return self.__autoRun( targetPos, self.__navExReachGoalFunctor, nearby )
		else:
			return False

	def isRunning( self ):
		"""
		判断navigate事件是否在运作中
		"""
		return self.__navExPathIndex > 0 or self.__purseEventID != 0

	def forceStop( self ):
		"""
		外部强制终止寻路事件的接口
		"""
		self.__stop()
		if self.needContinueLongSearch():
			self.clearSpaceDoorPath()
			self.__owner.endAutoRun( False )

	def getGoalPosition( self ):
		"""
		获取当前场景的目的点的坐标
		"""
		return len( self.__spaceDoorPath ) > 0 and Math.Vector3( self.__spaceDoorPath[0][1] ) or self.__spaceGoalPos

	def getPathList( self, goalPos ):
		"""
		获取到达目标点的寻路路径点列表
		生成当前场景,原位置到goalPos的路径
		注意:没有路径抵达goalPos时,会回调Action.onNavigateExNoPathFind接口
		@type			RETURN: bool
		@param			RETURN: 目的地是否可以抵达
		@type			goalPos: Vector3
		@param			goalPos: 目的点
		"""
		startPos = Math.Vector3( self.__owner.position )
		navMgr = NavDataMgr.instance()
		navExPath = navMgr.tryBestFindPath(startPos, goalPos, self.__owner.spaceID, True)
		if len(navExPath) < 1:
			self.__owner.onNavigateExNoPathFind( self.__navExState )
			self.forceStop()
		return navExPath


#-------------------------------------------------------------------------------
class NavDataMgr:

	Y_HACK			= 10
	X_Z_HACK		= 0.01

	_instance = None

	def __init__( self ):
		assert NavDataMgr._instance is None, "instance already exist in"

	def isNavDataReady( self ):
		"""
		判断navigate数据是否加载完毕
		"""
		return csol.navExLoadingProgress() == 1.0

	def isInWayPoint( self, testPos ):
		"""
		测试testPos是否位于一个waypoint内
		@type		testPos: Vector3
		@param		testPos: 待测试点
		"""
		return  self.isNavDataReady() and  csol.navExIsInWaypoint( testPos, 1.2 )

	def loadingProgress( self ):
		"""
		获取加载navigate数据进度, -1.0表示加载失败
		"""
		return csol.navExLoadingProgress()

	def loadNavData( self, spaceFloder, girth ):
		"""
		@type		spaceFloder: string
		@param		spaceFloder: 地图的文件夹名
		@type		girth: float
		@param		girth: 要加载的navigate数据的Girth值
		"""
		sp = "universes/%s/" % spaceFloder
		DEBUG_MSG( "loading NavData: %sNavMesh %d.%02d.bin" %( sp, int( girth ), int( ( girth - int( girth ) )* 100 ) ) )
		csol.navExLoadNavMesh( sp, girth, 0 )

	def canNavigateTo( self, srcPos, dstPos ):
		"""
		返回从srcPos可以到达dstPos附近且不同高度的点
		"""
		if not self.isNavDataReady():
			return []
		return csol.navExCanNavigateTo( srcPos, dstPos )

	def findSecPath( self, srcPos, dstPos, usePathFilter ):
		"""
		获取分段的路径,由于底层采用分时分层的A*搜索方案，故当最后一个节点非目的点时，需要继续调用该接口,
		@return		:成功时返回由Vector3组成的列表,失败时返回空列表
		@type		srcPos: Vector3
		@param		srcPos: 源点
		@type		dstPos: Vector3
		@param		dstPos: 目标点
		@type		usePathFilter: bool
		@param		usePathFilter: 是否采用路径过滤技术
		"""
		if not self.isNavDataReady():
			return []
		try:
			return csol.navExFindPath( srcPos, dstPos, usePathFilter )
		except:
			return []

	def simpleFindPath( self, srcPos, dstPos ):
		"""
		简单的路径搜索方式.
		注意：调用此接口时，需要确保目的点可以抵达(可以使用canNavigateTo接口来测试),
			 否则会消耗大量的时间来进行无意义的路径搜索
		@return		:成功时返回由Vector3组成的列表,失败时返回空列表
		@type		srcPos: Vector3
		@param		srcPos: 源点
		@type		dstPos: Vector3
		@param		dstPos: 目标点
		"""
		if not self.isNavDataReady():
			return []
		try:
			#curTime = time.time()
			path = csol.navExSimpleFindPath( srcPos, dstPos )
			#DEBUG_MSG( "=======>use", time.time() - curTime )
			return path
		except:
			return []

	def findFullPath( self, srcPos, dstPos, usePathFilter, timeOut = 0.5 ):
		"""
		获取从源点到目的点的全部路径
		@return		:成功时返回由Vector3组成的列表,失败时返回空列表
		@type		srcPos: Vector3
		@param		srcPos: 源点
		@type		dstPos: Vector3
		@param		dstPos: 目标点
		@type		usePathFilter: bool
		@param		usePathFilter: 是否采用路径过滤技术
		@type		timeOut: float
		@param		timeOut: 溢出的时间,单位秒(默认值:0.5秒)
		"""
		path = self.findSecPath( srcPos, dstPos, usePathFilter )
		if len( path ) == 0:
			return path #[]
		path.insert( 0, Math.Vector3( srcPos ) )
		saveTime = time.time()
		while True:
			curTime = time.time()
			timeOut -= ( curTime - saveTime )
			if timeOut < 0:
				DEBUG_MSG("=================================>TimeOut!")
				return []
			saveTime = curTime
			targetPos = path[-1]
			if dstPos.distTo( targetPos ) < 0.01:
				break
			nxtPath = self.findSecPath( targetPos, dstPos, usePathFilter )
			if len( nxtPath ) == 0:
				break
			path.extend( nxtPath )
		#DEBUG_MSG("=================================>CostTime:",  0.5 - timeOut )
		return path

	def clearNavData( self ):
		"""
		清空navigate数据, 释放内存
		"""
		csol.navExClear()

	def tryBestFindPath( self, startPos, goalPos, spaceID, adaptHeight=False ):
		"""
		获取到达目标点的寻路路径点列表
		生成当前场景,原位置到goalPos的路径
		@type			RETURN: bool
		@param			RETURN: 目的地是否可以抵达
		@type			srcPos: Vector3
		@param			srcPos: 目的点
		@type			goalPos: Vector3
		@param			goalPos: 目的点
		@type			adaptHeight: bool
		@param			adaptHeight: 是否允许尝试调整高度搜索路径
		"""
		navExPath = []         # 寻路节点列表
		if self.isReachGoal( startPos, goalPos ):
			return [goalPos]
		if self.isNavDataReady():
			goalPosLst = self.canNavigateTo( startPos, goalPos )

			#避免地图中带顶部NavMesh的封闭区域（如山洞）寻路时会获取错误y高度而造成寻路失败的问题 by cxm 2010.10.15
			if len( goalPosLst ) == 0 and adaptHeight:
				newGoal = Math.Vector3(goalPos.x, startPos.y, goalPos.z)
				goalPosLst = self.canNavigateTo( startPos, newGoal )

			if len( goalPosLst ) > 0:
				canReachGoal = self.__getBestGoalPos( goalPosLst, goalPos, spaceID )
				path = self.simpleFindPath( startPos, canReachGoal )
				if len( path ) > 0:
					navExPath.extend( path )

			if len( navExPath ) < 1:
				srcNearDst = self.__getSrcAndNearDstPos( startPos, goalPos )
				if srcNearDst is not None:
					canReachGoal = self.__getBestGoalPos( srcNearDst[1], goalPos, spaceID )
					path = self.simpleFindPath( startPos, canReachGoal )
					if len( path ) > 0:
						navExPath.extend( path )
						navExPath.append( goalPos )

			#default search
			if len( navExPath ) < 1:
				path = self.findFullPath( startPos, goalPos, False )
				if len( path ) > 0:
					navExPath.extend( path )

		else:
			navExPath = [startPos, goalPos]

		return navExPath

	def isReachGoal( self, curPos, goalPos ):
		"""
		判断是否抵达目的点
		@type		curPos: Vector3
		@param		curPos: 当前点
		@type		goalPos: Vector3
		@param		goalPos: 目的点
		"""
		targetPos = Math.Vector3( goalPos )
		targetPos.y = curPos.y
		if targetPos.distTo( curPos ) < NavDataMgr.X_Z_HACK and  math.fabs( curPos.y - goalPos.y ) < NavDataMgr.Y_HACK:
			return True
		return False

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getBestGoalPos( self, goalPosLst, testPos, spaceID ):
		"""
		获取最佳的目的点
		@type		return: Vector3
		@param		return: 最佳的目的点
		@type		goalPosLst: list of Vector3
		@param		goalPosLst: 可以到达的目的点列表
		@type		testPos: Vector3
		@param		testPos: 测试点
		"""
		gPos = self.__findDropPoint( spaceID, testPos )
		minYOffset = 999999
		bestPos = gPos
		for p in goalPosLst:
			curYOffset = math.fabs( p.y - gPos.y )
			if curYOffset < minYOffset:
				minYOffset = curYOffset
				bestPos = Math.Vector3( p )
		return bestPos

	def __getSrcAndNearDstPos( self, srcPos, dstPos ):
		"""
		返回srcPos和可以抵达dstPos附近的点组成的元组(Vector3， [Vector3, ...]), 没有找到时，返回None
		@type			srcPos: Vector3
		@param			srcPos: 源点
		@type			dstPos: Vector3
		@param			dstPos: 目标点
		"""
		navMgr = NavDataMgr.instance()
		if not navMgr.isNavDataReady():
			return None
		anglePi = math.pi/4.0
		testSrcPos = Math.Vector3(0, 0, 0)
		L = 4
		for ln in xrange( 1, L + 1 ):
			for s in xrange( 8 ):
				sn = s*anglePi
				testSrcPos.y = dstPos.y + 2
				testSrcPos.x = dstPos.x + ln * math.sin( sn )
				testSrcPos.z = dstPos.z + ln * math.cos( sn )
				goalPosLst = navMgr.canNavigateTo( srcPos, testSrcPos )
				if len( goalPosLst ) > 0:
					return ( testSrcPos, goalPosLst )
		return None

	def __findDropPoint( self, spaceID, point ):
		"""
		拾取地面处理
		@type		point: Vector3
		@param		point: 有待拾取地面的点
		"""
		testPos = Math.Vector3( point )
		testPos.y += 3
		dp = BigWorld.findDropPoint( spaceID, testPos )
		if dp is not None:
			testPos.y = dp[0].y
		else:
			testPos.y = point.y
		return testPos


	@staticmethod
	def instance():
		"""
		返回NavDataMgr单件的实例
		"""
		if NavDataMgr._instance is None:
			NavDataMgr._instance = NavDataMgr()
		return NavDataMgr._instance

