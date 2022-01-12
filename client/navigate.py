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
	#"����"����
	IGNORE_LEN 		= 0.5
	IGNORE_ANGLE 	= math.pi / 4
	INVALIDITY_POS	= Math.Vector3( -100000000, -100000000, -100000000 ) #��־Ϊ��Ч��ֵ
	#״̬����,ע����Щ״̬���Ṳ��
	NAV_STATE_NONE			= 0				#��״̬
	NAV_STATE_PURSUE		= 1				#����״̬
	NAV_STATE_MCTRL			= 2				#mouseCtrlRun
	NAV_STATE_SDEST			= 3				#triggerRunͬһ����Ѱ·
	NAV_STATE_LDEST			= 4				#triggerRun�糡��Ѱ·
	NAV_STATE_TRAP 			= 5				#Ѱ·��λ:��ʼʱ����������,�����԰�
	def __init__( self, owner ):
		self.__owner = weakref.proxy( owner, self.__onOwnerLost )
		self.__navExPath = [] #ʵ�ʵ�·��
		self.__perfectPath = [] #��������ʾ��·��
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
		"""owner��������"""
		self.__stop()
		if self.needContinueLongSearch():
			self.clearSpaceDoorPath()

	def __onCollisionCBF( self ):
		"""
		�Զ�Ѱ·״̬�У������ϰ�����޷��ߵ��Ļص�����
		"""
		self.__onGoalReach( False )

	def __onEnterNavState( self, navState ):
		"""
		����ĳ��״̬ʱ,�����˺���
		@type		navState: NAV_STATE TYPE
		@param		navState: NAV_STATE
		"""
		self.__navExState = navState

	def __findDropPoint( self, point ):
		"""
		ʰȡ���洦��
		@type		point: Vector3
		@param		point: �д�ʰȡ����ĵ�
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
		���ڳ���ԭ�򣬿�λ�޷��ƶ������
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
		ȡ��trapDetect�¼�
		"""
		if self.__trapDetectEventID != 0:
			BigWorld.cancelCallback( self.__trapDetectEventID )
			self.__trapDetectEventID = 0

	def __onGoalReach( self, isSuccess ):
		"""
		�ִ�Ŀ�ĵ�ʱ�Ļص�����
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
		if self.__navExPathIndex < pathLen - 1: #·��������Զ��
			callback = self.__navExGo
			isSeekToGoal = False
		elif self.__navExPathIndex == pathLen - 1: #����ڼ�
			callback = self.__onGoalReach
			isSeekToGoal = True
			self.__cancelTrapDetect()
			self.__owner.getPhysics().setSeekCollisionCallBackFn( self.__onCollisionCBF )
		else: #�ִ�Ŀ�ĵ�ʱ
			self.__onGoalReach( True )
			return
		dstPos = self.__findDropPoint( self.__navExPath[self.__navExPathIndex] )
		self.__owner.seek( dstPos, 1000, callback, isSeekToGoal )

	def __stop( self ):
		"""
		ֹͣѰ·�¼�
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
		����Ѱ·��Ŀ��㸽����������
		@type		nearby:        float
		@param		nearby:        �ƶ���Ŀ��λ�ø����ľ���
		@type		dstSpaceLabel: string
		@param		dstSpaceLabel: Ŀ��Space Name
		"""
		if not self.needContinueLongSearch() or dstSpaceLabel != "":
			self.__spaceNearBy = nearby

	def __getNearBy( self ):
		"""
		��ȡ��ǰ������,Ѱ·��Ŀ��㸽����������
		"""
		if self.needContinueLongSearch():
			return 0
		else:
			return self.__spaceNearBy

	def __onNearbyCheck( self ):
		"""
		���ص��¼�
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
		�ƶ���Ŀ��λ�ø��������
		@type			nearby: float
		@param			nearby: �ƶ���Ŀ��λ�ø����ľ���(��λm)
		"""
		self.__curNearBy = nearby
		if self.__curNearBy > 0:
			self.__onNearbyCheck()

	def __onPursueOver( self, callback, isSuccess ):
		"""
		pursue�¼���·�����ʱ�Ļص�����
		@type		callback:  Functor
		@param		callback:  �ص�����
		@type		isSuccess: bool
		@param		isSuccess: �Ƿ�ִ�Ŀ�ĵ�
		"""
		if callable( callback ):
			callback( isSuccess )
		self.__onPursueEvent()

	def __onPursuePosOver( self, callback, isSuccess ):
		"""
		pursue�¼���·�����ʱ�Ļص�����
		@type		callback:  Functor
		@param		callback:  �ص�����
		@type		isSuccess: bool
		@param		isSuccess: �Ƿ�ִ�Ŀ�ĵ�
		"""
		if callable( callback ):
			callback( isSuccess )
		# ���µ�����һ���汾��BigWorld.callback(0,__onPursuePosEvent)
		# ���������ʽ�����׺�pursueEntity������ͻ��������������
		# BigWorld.callback(0,__onPursuePosEvent)֮���ڻص�����ǰ��
		# ��pursueEntity׷�٣����Żص������ˣ���ʱ__onPursuePosEvent��
		# �ص������ݽ���pursueEntity���õ����ݣ������ص��������ǵ���
		# pursuePositionʱ���õĺ���������pursueEntity���õĺ��������
		# �ص������ݳ�������Ԥ�ڲ��������
		self.__onPursuePosEvent()

	def __onPursueEvent( self ):
		"""
		pursue�ص��¼�
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
		pursue�ص��¼�
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
		����L���ڣ����Ե������λ��waypoint�ڵ�λ��
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
		����srcPos�Ϳ��Եִ�dstPos�����ĵ���ɵ�Ԫ��(Vector3�� [Vector3, ...]), û���ҵ�ʱ������None
		@type			srcPos: Vector3
		@param			srcPos: Դ��
		@type			dstPos: Vector3
		@param			dstPos: Ŀ���
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
		��ȡ��ѵ�Ŀ�ĵ�
		@type		return: Vector3
		@param		return: ��ѵ�Ŀ�ĵ�
		@type		goalPosLst: list of Vector3
		@param		goalPosLst: ���Ե����Ŀ�ĵ��б�
		@type		testPos: Vector3
		@param		testPos: ���Ե�
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
		���ɵ�ǰ����,ԭλ�õ�goalPos��·��
		ע��:û��·���ִ�goalPosʱ,��ص�Action.onNavigateExNoPathFind�ӿ�
		@type			RETURN: bool
		@param			RETURN: Ŀ�ĵ��Ƿ���Եִ�
		@type			goalPos: Vector3
		@param			goalPos: Ŀ�ĵ�
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
		����Ŀ���
		@type		RETURN: bool
		@param		RETURN: Ŀ�ĵ��Ƿ���Եִ�
		@type		pos: Vector3
		@param		pos: Ŀ���
		@type		dstSpaceLabel: string
		@param		dstSpaceLabel: Ŀ��Space Name
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
		@param			RETURN: Ŀ�ĵ��Ƿ���Եִ�
		@type			goalPos: Vector3
		@param			goalPos: Ѱ·��ָ���ĵ�
		@type 			reachGoalCallBack: func
		@param			reachGoalCallBack: �ִ�Ŀ�ĵ�ʱ�Ļص�����
		@type			nearby: float
		@param			nearby: �ƶ���Ŀ��λ�ø����ľ���
		@type			dstSpaceLabel: string
		@param			dstSpaceLabel: Ŀ�곡����ǩ��
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
		��������ƶ�����
		@type			RETURN: bool
		@param			RETURN: Ŀ�ĵ��Ƿ���Եִ�
		@type			goalPos: Vector3
		@param			goalPos: Ѱ·��ָ���ĵ�
		@type 			reachGoalCallBack: func
		@param			reachGoalCallBack: �ִ�Ŀ�ĵ�ʱ�Ļص�����
		"""
		self.__onEnterNavState( NavigateEx.NAV_STATE_MCTRL )
		return self.__autoRun( goalPos, reachGoalFunctor )

	def triggerRun( self, goalPos, reachGoalFunctor,  nearby = 0.0,  dstSpaceLabel = "" ):
		"""
		���������¼����ƶ�����
		@type			RETURN: bool
		@param			RETURN: Ŀ�ĵ��Ƿ���Եִ�
		@type			goalPos: Vector3
		@param			goalPos: Ѱ·��ָ���ĵ�
		@type 			reachGoalCallBack: func
		@param			reachGoalCallBack: �ִ�Ŀ�ĵ�ʱ�Ļص�����
		@type			nearby: float
		@param			nearby: �ƶ���Ŀ��λ�ø����ľ���
		@type			dstSpaceLabel: string
		@param			dstSpaceLabel: Ŀ�곡����ǩ��
		"""
		srcSpaceLabel = BigWorld.player().getSpaceLabel()
		if srcSpaceLabel == dstSpaceLabel:
			dstSpaceLabel = "" #Ŀ����ڵ�ǰ�����������ÿ糡������

		if dstSpaceLabel == "":
			self.__onEnterNavState( NavigateEx.NAV_STATE_SDEST )
		else:
			self.__onEnterNavState( NavigateEx.NAV_STATE_LDEST )
		return self.__autoRun( goalPos, reachGoalFunctor, nearby, dstSpaceLabel )

	def getNavPosLst( self ):
		"""
		���˳���С��IGNORE_LEN���߶Σ�������������LineGUIComponent����ʱ�����ֵ��ص������
		���˼н�С��IGNORE_ANGLE�Ķ���, ������������LineGUIComponent����ʱ�����ֳ����ߵ����
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
		����һ��Ŀ��
		@type			target: instance
		@param			target: entity you want to pursue
		@type			nearby: float
		@param			nearby: ����Ŀ��λ�ø��������ױ�ͣ����
		@type			callback: callback functor
		@param			callback: ��ɸ��ٺ�Ļص�����
		"""
		self.__onEnterNavState( NavigateEx.NAV_STATE_PURSUE )
		self.__purseCheckCount = 888
		self.__pursueTarget = target
		self.__pauseNearby = nearby
		self.__pauseCallback = callback
		self.__onPursueEvent()

	def pursuePosition( self, pos, nearby, callback ):
		"""
		����һ��Ŀ��
		@type			target: instance
		@param			target: entity you want to pursue
		@type			nearby: float
		@param			nearby: ����Ŀ��λ�ø��������ױ�ͣ����
		@type			callback: callback functor
		@param			callback: ��ɸ��ٺ�Ļص�����
		"""
		self.__onEnterNavState( NavigateEx.NAV_STATE_PURSUE )
		self.__purseCheckCount = 888
		self.__pursuePos = pos
		self.__pauseNearby = nearby
		self.__pauseCallback = callback
		self.__onPursuePosEvent()

	def needContinueLongSearch( self ):
		"""
		�ж��Ƿ�������г�����Ѱ·
		"""
		return len( self.__spaceDoorPath ) != 0

	def clearSpaceDoorPath( self ):
		"""
		��տ糡��Ѱ·��Ϣ����
		"""
		self.__spaceDoorPath = []

	def tryContinueLongSearch( self ):
		"""
		���Լ���������Ѱ·���ɹ�����True��ʧ�ܷ���False
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
		�ж�navigate�¼��Ƿ���������
		"""
		return self.__navExPathIndex > 0 or self.__purseEventID != 0

	def forceStop( self ):
		"""
		�ⲿǿ����ֹѰ·�¼��Ľӿ�
		"""
		self.__stop()
		if self.needContinueLongSearch():
			self.clearSpaceDoorPath()
			self.__owner.endAutoRun( False )

	def getGoalPosition( self ):
		"""
		��ȡ��ǰ������Ŀ�ĵ������
		"""
		return len( self.__spaceDoorPath ) > 0 and Math.Vector3( self.__spaceDoorPath[0][1] ) or self.__spaceGoalPos

	def getPathList( self, goalPos ):
		"""
		��ȡ����Ŀ����Ѱ··�����б�
		���ɵ�ǰ����,ԭλ�õ�goalPos��·��
		ע��:û��·���ִ�goalPosʱ,��ص�Action.onNavigateExNoPathFind�ӿ�
		@type			RETURN: bool
		@param			RETURN: Ŀ�ĵ��Ƿ���Եִ�
		@type			goalPos: Vector3
		@param			goalPos: Ŀ�ĵ�
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
		�ж�navigate�����Ƿ�������
		"""
		return csol.navExLoadingProgress() == 1.0

	def isInWayPoint( self, testPos ):
		"""
		����testPos�Ƿ�λ��һ��waypoint��
		@type		testPos: Vector3
		@param		testPos: �����Ե�
		"""
		return  self.isNavDataReady() and  csol.navExIsInWaypoint( testPos, 1.2 )

	def loadingProgress( self ):
		"""
		��ȡ����navigate���ݽ���, -1.0��ʾ����ʧ��
		"""
		return csol.navExLoadingProgress()

	def loadNavData( self, spaceFloder, girth ):
		"""
		@type		spaceFloder: string
		@param		spaceFloder: ��ͼ���ļ�����
		@type		girth: float
		@param		girth: Ҫ���ص�navigate���ݵ�Girthֵ
		"""
		sp = "universes/%s/" % spaceFloder
		DEBUG_MSG( "loading NavData: %sNavMesh %d.%02d.bin" %( sp, int( girth ), int( ( girth - int( girth ) )* 100 ) ) )
		csol.navExLoadNavMesh( sp, girth, 0 )

	def canNavigateTo( self, srcPos, dstPos ):
		"""
		���ش�srcPos���Ե���dstPos�����Ҳ�ͬ�߶ȵĵ�
		"""
		if not self.isNavDataReady():
			return []
		return csol.navExCanNavigateTo( srcPos, dstPos )

	def findSecPath( self, srcPos, dstPos, usePathFilter ):
		"""
		��ȡ�ֶε�·��,���ڵײ���÷�ʱ�ֲ��A*�����������ʵ����һ���ڵ��Ŀ�ĵ�ʱ����Ҫ�������øýӿ�,
		@return		:�ɹ�ʱ������Vector3��ɵ��б�,ʧ��ʱ���ؿ��б�
		@type		srcPos: Vector3
		@param		srcPos: Դ��
		@type		dstPos: Vector3
		@param		dstPos: Ŀ���
		@type		usePathFilter: bool
		@param		usePathFilter: �Ƿ����·�����˼���
		"""
		if not self.isNavDataReady():
			return []
		try:
			return csol.navExFindPath( srcPos, dstPos, usePathFilter )
		except:
			return []

	def simpleFindPath( self, srcPos, dstPos ):
		"""
		�򵥵�·��������ʽ.
		ע�⣺���ô˽ӿ�ʱ����Ҫȷ��Ŀ�ĵ���Եִ�(����ʹ��canNavigateTo�ӿ�������),
			 ��������Ĵ�����ʱ���������������·������
		@return		:�ɹ�ʱ������Vector3��ɵ��б�,ʧ��ʱ���ؿ��б�
		@type		srcPos: Vector3
		@param		srcPos: Դ��
		@type		dstPos: Vector3
		@param		dstPos: Ŀ���
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
		��ȡ��Դ�㵽Ŀ�ĵ��ȫ��·��
		@return		:�ɹ�ʱ������Vector3��ɵ��б�,ʧ��ʱ���ؿ��б�
		@type		srcPos: Vector3
		@param		srcPos: Դ��
		@type		dstPos: Vector3
		@param		dstPos: Ŀ���
		@type		usePathFilter: bool
		@param		usePathFilter: �Ƿ����·�����˼���
		@type		timeOut: float
		@param		timeOut: �����ʱ��,��λ��(Ĭ��ֵ:0.5��)
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
		���navigate����, �ͷ��ڴ�
		"""
		csol.navExClear()

	def tryBestFindPath( self, startPos, goalPos, spaceID, adaptHeight=False ):
		"""
		��ȡ����Ŀ����Ѱ··�����б�
		���ɵ�ǰ����,ԭλ�õ�goalPos��·��
		@type			RETURN: bool
		@param			RETURN: Ŀ�ĵ��Ƿ���Եִ�
		@type			srcPos: Vector3
		@param			srcPos: Ŀ�ĵ�
		@type			goalPos: Vector3
		@param			goalPos: Ŀ�ĵ�
		@type			adaptHeight: bool
		@param			adaptHeight: �Ƿ������Ե����߶�����·��
		"""
		navExPath = []         # Ѱ·�ڵ��б�
		if self.isReachGoal( startPos, goalPos ):
			return [goalPos]
		if self.isNavDataReady():
			goalPosLst = self.canNavigateTo( startPos, goalPos )

			#�����ͼ�д�����NavMesh�ķ��������ɽ����Ѱ·ʱ���ȡ����y�߶ȶ����Ѱ·ʧ�ܵ����� by cxm 2010.10.15
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
		�ж��Ƿ�ִ�Ŀ�ĵ�
		@type		curPos: Vector3
		@param		curPos: ��ǰ��
		@type		goalPos: Vector3
		@param		goalPos: Ŀ�ĵ�
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
		��ȡ��ѵ�Ŀ�ĵ�
		@type		return: Vector3
		@param		return: ��ѵ�Ŀ�ĵ�
		@type		goalPosLst: list of Vector3
		@param		goalPosLst: ���Ե����Ŀ�ĵ��б�
		@type		testPos: Vector3
		@param		testPos: ���Ե�
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
		����srcPos�Ϳ��Եִ�dstPos�����ĵ���ɵ�Ԫ��(Vector3�� [Vector3, ...]), û���ҵ�ʱ������None
		@type			srcPos: Vector3
		@param			srcPos: Դ��
		@type			dstPos: Vector3
		@param			dstPos: Ŀ���
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
		ʰȡ���洦��
		@type		point: Vector3
		@param		point: �д�ʰȡ����ĵ�
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
		����NavDataMgr������ʵ��
		"""
		if NavDataMgr._instance is None:
			NavDataMgr._instance = NavDataMgr()
		return NavDataMgr._instance

