# -*- coding: gb18030 -*-

import csstatus
import csconst
import csdefine
import Const
import ECBExtend
import random
import cschannel_msgs
from bwdebug import *
import Resource.BoardEventLoader
from config.server.ChessBoardData import Datas as g_boardData

g_boardEvent = Resource.BoardEventLoader.g_boardEventLoader()

ENTERN_DESTINY_TRANS_MENBER_DISTANCE = 30.0	# 队伍搜索范围

class RoleDestinyTransInterface:
	"""
	 天命轮回副本接口
	 """
	def __init__( self ):
		pass

	def roleEnterDestinyTransCheck( self, reqLevel ):
		"""
		define method
		玩家进入天命轮回副本前检测
		"""
		if not self.isTeamCaptain():
			# 不是队长
			self.statusMessage( csstatus.DESTINY_TRANS_NOT_CAPTAIN )
			return
		
		if not self.teamMemberComCheck( reqLevel ):
			# 队伍成员条件判断
			return
		
		self.destinyTransSpaceEnter()
	
	def teamMemberComCheck( self, reqLevel ):
		"""
		队伍成员条件判断
		"""
		# 距离判断
		teamMemberIDs = self.getAllIDNotInRange( ENTERN_DESTINY_TRANS_MENBER_DISTANCE )
		if len( teamMemberIDs ) > 0:
			for id in teamMemberIDs:
				self.client.teamNotifyWithMemberName( csstatus.TEAM_MEMBER_NOT_IN_RANGE, id )
			return False
		
		# 等级、进入次数判断
		roleList = self.getAllMemberInRange( ENTERN_DESTINY_TRANS_MENBER_DISTANCE )
		lowLevelMembersStr = ""
		enteredMembersStr = ""
		for i in roleList:
			if i.level < reqLevel:
				lowLevelMembersStr += ( i.getName() + "," )
			if i.isActivityCanNotJoin( csdefine.ACTIVITY_DENTITY_TRANS_COM ) :
				enteredMembersStr += ( i.getName() + "," )
		
		if lowLevelMembersStr != "":
			# 队伍中有人级别不够
			self.statusMessage( csstatus.DESTINY_TRANS_LEVEL_NOT_ENOUGH, lowLevelMembersStr )
			return False
		
		if enteredMembersStr != "":
			# 队伍中有人参加天命副本的次数已满
			self.statusMessage( csstatus.DESTINY_TRANS_ENTER_FULL, enteredMembersStr )
			return False
		
		return True

	def destinyTransSpaceEnter( self ):
		"""
		请求开启天命轮回副本
		"""
		teamMemberList = self.getAllMemberInRange( ENTERN_DESTINY_TRANS_MENBER_DISTANCE )
		playerList, dbidList = [], []
		for m in teamMemberList:
			# 防止出现重复的情况
			if m.id not in [ e.id for e in playerList ]:
				playerList.append( m.base )
				dbidList.append( m.databaseID )
				m.set( "destityTransSpaceType", csconst.DESTINY_TRANS_COPY_COMMON )
		
		BigWorld.globalData[ "SpaceDestinyTransMgr" ].onRequestDestinyTransCom( playerList, dbidList, self.teamMailbox.id )

	def destinyTransSpaceStart( self, chessboardNo, gateInfo, livePointInfo, destinyTransKey ):
		"""
		define method
		天命副本开启
		chessboardNo: 棋盘编号
		gateInfo: 成员关卡信息
		"""
		self.setTemp( "destinyTransKey", destinyTransKey )
		self.setTemp( "chessboardNo", chessboardNo )
		self.setTemp( "chessPos", gateInfo[ self.databaseID ] )
		self.setTemp( "livePoint", livePointInfo[ self.databaseID ] )
		
		self.addActivityCount( csdefine.ACTIVITY_DENTITY_TRANS_COM )
		self.setCurPosRevivePos()									# 设置当前位置为复活位置，避免通关失败后被传送到城市复活点

		self.openBoardInterface( chessboardNo, gateInfo, livePointInfo )

	def openBoardInterface( self, chessboardNo, gateInfo, livePointInfo ):
		"""
		define method
		打开棋盘界面
		"""
		INFO_MSG( "DESTRANS_LOG: %s 's current spaceType is %s, last spaceType is %s" % ( self.getNameAndID(), self.spaceType, self.queryTemp( "last_space_type", 0 ) ) )
		self.client.openBoardInterface( chessboardNo, gateInfo, livePointInfo )	# 打开棋盘界面

		if self.queryTemp( "livePoint", 0 ) < 0: # 如果玩家的复活点数为0，则不再自动掷筛子
			return
		
		if not gateInfo[ self.databaseID ][ 1 ] and gateInfo[ self.databaseID ][ 0 ]:	# 未通关且非起点，则进入关卡
			INFO_MSG( "DESTRANS_LOG: %s:Gate %s has not finished yet, reEnter. BoardNo is %i " % ( self.getNameAndID(), gateInfo[ self.databaseID ], chessboardNo ) )
			self.endMoveChess( self.id )
		else:
			self.addSysThrowSieveTimer()							# 开始倒计时

	def reOpenBoardInterface( self, chessboardNo, gateInfo, livePointInfo, destinyTransKey ):
		"""
		define method
		玩家上线重新打开棋盘界面
		"""
		self.setTemp( "destinyTransKey", destinyTransKey )
		self.setTemp( "chessboardNo", chessboardNo )
		self.setTemp( "chessPos", gateInfo[ self.databaseID ] )
		self.setTemp( "livePoint", livePointInfo[ self.databaseID ] )
		
		self.openBoardInterface( chessboardNo, gateInfo, livePointInfo )

	def addSysThrowSieveTimer( self ):
		"""
		添加自动掷筛子timer
		"""
		if self.queryTemp( "livePoint", 0 ) < 0: # 如果玩家的复活点数为0，则不再自动掷筛子
			return
		autoThrowTimer = self.addTimer( Const.AUTO_THROW_SIEVE_TIME, 0, ECBExtend.AUTO_THROW_SIEVE_TIMER_CBID )
		self.setTemp( "autoThrowTimer", autoThrowTimer )
		self.client.onCountDown( Const.AUTO_THROW_SIEVE_TIME )

	def onAutoThrowSieve( self, controllerID, userData ):
		"""
		自动掷筛子
		"""
		point = random.randint( 1, 6 )
		self.setTemp( "SIEVE_POINT", point )
		self.client.onGetSievePoint( point )		# 通知客户端播放动画

	def throwSieve( self, srcEntityID ):
		"""
		Exposed Mehod
		客户端申请掷筛子
		"""
		if not self.hackVerify_( srcEntityID ):
			return
		
		autoThrowTimer = self.queryTemp( "autoThrowTimer", 0 )
		if autoThrowTimer:
			self.cancel( autoThrowTimer )
		
		point = random.randint( 1, 6 )
		self.setTemp( "SIEVE_POINT", point )
		self.client.onGetSievePoint( point )		# 通知客户端播放动画

	def endPlaySieveAnimation( self, srcEntityID ):
		"""
		Exposed Method
		客户端播放掷筛子动画结束，开始移动棋子
		"""
		if not self.hackVerify_( srcEntityID ):
			return
		
		point = self.queryTemp( "SIEVE_POINT", 0 )
		self.moveChess( point )

	def moveChess( self, point ):
		"""
		移动棋子
		"""
		oldChessPos = self.queryTemp( "chessPos", 0 )
		chessboardNo = self.queryTemp( "chessboardNo", 0 )
		if not chessboardNo:
			ERROR_MSG( "%s 's chess board number is 0 " % self.getNameAndID() )
			return
		
		chessPos = [ 0, 0 ]
		chessPos[0] = min( max( 0, oldChessPos[0] + point ), len( g_boardData[ chessboardNo ] ) - 1 )
		
		eventID = g_boardData[ chessboardNo ][ chessPos[0] ]
		event = g_boardEvent.__getitem__( eventID )
		if event.type == csdefine.CHESS_BOARD_EVE_MOVE:
			chessPos[ 1 ] = 1

		self.setTemp( "chessPos", chessPos )
		# 通知管理器
		BigWorld.globalData[ "SpaceDestinyTransMgr" ].updateRoleGateInfo( self.base, self.databaseID, self.teamMailbox.id, chessPos )

	def endMoveChess( self, srcEntityID ):
		"""
		Exposed Mehod
		移动棋子结束，开始触发关卡
		"""
		if not self.hackVerify_( srcEntityID ):
			return
		
		chessPos = self.queryTemp( "chessPos", [ 0, 0] )
		if chessPos[0] <= 0:
			self.addSysThrowSieveTimer()					# 开始倒计时
			self.client.onCountDown( Const.AUTO_THROW_SIEVE_TIME )
		else:
			self.triggerBoardEvent()

	def triggerBoardEvent( self ):
		"""
		触发棋盘事件
		"""
		chessPos = self.queryTemp( "chessPos", [ 0, 0 ] )
		chessboardNo = self.queryTemp( "chessboardNo", 0 )
		if not chessboardNo:
			ERROR_MSG( "DESTRANS_LOG:%s 's chess board number is 0 " % self.getNameAndID() )
			return
		
		eventID = g_boardData[ chessboardNo ][ chessPos[0] ]
		event = g_boardEvent.__getitem__( eventID )
		event.do( self )

	def enterDestinyTransGate( self, eventType, eventID ):
		"""
		进入关卡
		"""
		self.setTemp( "DESTINY_EVENT_ID", eventID )
		BigWorld.globalData[ "SpaceDestinyTransMgr" ].roleReqEnterDestinyGate( eventType, self.base )

	def getBoardEvent( self ):
		"""
		获取棋盘事件
		"""
		eventID = self.queryTemp( "DESTINY_EVENT_ID",0 )
		if not eventID:
			return 
		event = g_boardEvent[eventID]
		return event

	def onEnterDestinyTransGate( self ):
		"""
		define mehod
		进入关卡内
		"""
		event = self.getBoardEvent()
		if not event:
			return
		event.triggerExtraEffect( self )

	def onLeaveDestinyTransGate( self ):
		"""
		define method
		离开关卡
		"""
		event = self.getBoardEvent()
		if not event:
			return
		event.endExtraEffect( self )

	def onPassedGate( self ):
		"""
		define method 
		完成关卡
		"""
		self.onLeaveDestinyTransGate()
		self.client.desTrans_msgs( csdefine.DESTINY_TRANS_FINISH_GATE )

		chessPos = self.queryTemp( "chessPos", [ 0, 0 ] )
		chessPos[ 1 ] = 1
		self.setTemp( "chessPos", chessPos )
		BigWorld.globalData[ "SpaceDestinyTransMgr" ].onRolePassedGate( self.base, self.databaseID, self.teamMailbox.id )

	def onFailedGate( self ):
		"""
		define method
		通关失败
		"""
		self.onLeaveDestinyTransGate()
		self.client.desTrans_msgs( csdefine.DESTINY_TRANS_FAILED_GATE )
		self.addLivePoint( -1 )

	def addLivePoint( self, value ):
		"""
		添加复活点，负数表示减去复活点数
		"""
		livePoint = self.queryTemp( "livePoint", 0 ) + value
		if livePoint < -1:
			return
		self.setTemp( "livePoint", livePoint )
		BigWorld.globalData["SpaceDestinyTransMgr"].onRoleLivePointChanged( self.base, self.databaseID, self.teamMailbox.id, livePoint )

	def roleReviveCostLivePoint( self, srcEntityID ):
		"""
		Exposed Method
		玩家点击复活按钮
		"""
		if not self.hackVerify_( srcEntityID ):
			return
		autoReviveTimer = self.queryTemp( "autoReviveTimer", 0 )
		if autoReviveTimer:
			self.cancel( autoReviveTimer )
		self.reviveCostLivePoint( )

	def reviveCostLivePoint( self, controllerID = 0 , userData = "" ):
		"""
		消耗复活点复活(目前只在天命轮回副本中使用)
		"""
		self.addLivePoint( -1 )
		self.tombPunish()
		self.changeState( csdefine.ENTITY_STATE_FREE )
		self.setHP( self.HP_Max )
		self.setMP( self.MP_Max )
		self.onRevive()
		self.reTriggerNearTrap()

	def onDestroy( self ):
		"""
		玩家下线
		"""
		destinyTransKey = self.queryTemp( "destinyTransKey", "" )
		if destinyTransKey:
			BigWorld.globalData["SpaceDestinyTransMgr"].onRoleDestroy( self.base, destinyTransKey )

	def onTime_RoleRevivePreSpace( self, controllerID, userData ):
		"""
		通关失败,复活
		"""
		self.addLivePoint( -1 )
		self.revive( self.id, csdefine.REVIVE_PRE_SPACE )

	def dt_onLeaveTeam( self ):
		"""
		离队处理
		"""
		destinyTransKey = self.queryTemp( "destinyTransKey", "" )
		if destinyTransKey:
			BigWorld.globalData["SpaceDestinyTransMgr"].onRoleLeaveTeam( self.base,self.databaseID, destinyTransKey )

	def dt_onLeaveTeamCB( self ):
		"""
		define method
		离队回调
		"""
		self.resetDestinyTransData()

	def resetDestinyTransData( self ):
		"""
		define method
		清除副本数据
		"""
		self.onLeaveDestinyTransGate()
		self.removeTemp( "destinyTransKey" )
		self.removeTemp( "chessboardNo" )
		self.removeTemp( "chessPos" )
		self.removeTemp( "livePoint" )
		self.removeTemp( "autoThrowTimer" )
		self.removeTemp( "autoReviveTimer" )
		self.removeTemp( "last_space_type" )
		self.removeTemp( "SIEVE_POINT" )
		self.removeTemp( "DESTINY_EVENT_ID" )
		self.remove( "destityTransSpaceType" )
		self.client.closeBoardInterface( 1 )

	def onPassedAllGate( self ):
		"""
		define method
		通关
		"""
		self.resetDestinyTransData()

	def destinyTransCheck( self ):
		"""
		从天命轮回副本传送出来时，需要根据读条是否完成来打开棋盘界面
		"""
		destinyTransKey = self.queryTemp( "destinyTransKey", "" )
		if destinyTransKey and self.teamMailbox:
			INFO_MSG( "DESTRANS_LOG: %s 's current spaceType is %s, last spaceType is %s" % ( self.getNameAndID(), self.spaceType, self.queryTemp( "last_space_type", 0 ) ) )
			if self.queryTemp( "last_space_type", 0 ) == csdefine.SPACE_TYPE_DESTINY_TRANS:
				self.requestOpenBoardInterface()
			else:
				self.client.closeBoardInterface( 0 )
		self.removeTemp( "last_space_type" )

	def requestOpenBoardInterface( self ):
		"""
		关卡结束请求打开棋盘界面
		"""
		BigWorld.globalData[ "SpaceDestinyTransMgr" ].roleReqOpenBoardInterface( self.base, self.teamMailbox.id )
