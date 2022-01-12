# -*- coding: gb18030 -*-

import BigWorld
import random
import uuid
import csconst
import csdefine
import csstatus
import cschannel_msgs
from bwdebug import *

GATE_TYPE_COM = 1
GATE_TYPE_BOSS = 2

class DestinyTransItem( object ):
	"""
	单个天命轮回副本
	"""
	def __init__( self, mgr ):
		self.mgr = mgr
		self.type = 0
		self.destinyManager = mgr				# 管理器
		self.chessboardNo = 0					# 棋盘编号
		self.uidKey = str( uuid.uuid1() )

	def getUIDKey( self ):
		"""
		获取副本唯一标识
		"""
		return self.uidKey

class DestinyTransItemCom( DestinyTransItem ):
	"""
	普通模式
	"""
	def __init__( self, mgr ):
		"""
		"""
		DestinyTransItem.__init__( self, mgr )
		self.type = csdefine.ACTIVITY_DENTITY_TRANS_COM
		self.gateInfo = {}						# { playerBDID:( gateNo, hasFinish ),playerBDID:( gateNo, hasFinish ), }
		self.winnerDBID = 0						# 第一个通关玩家
		self.playerEntities = []
		self.livePointInfo = {}
		self.teamID = 0

	def start( self ):
		"""
		开启副本
		"""
		for playerMB in self.playerEntities:
			playerMB.cell.destinyTransSpaceStart( self.chessboardNo, self.gateInfo, self.livePointInfo, self.uidKey )

	def updateGateInfo( self, playerBDID, playerMB, boardPos ):
		"""
		更新角色棋盘位置信息
		"""
		if playerMB.id not in [ mb.id for mb in self.playerEntities ]:
			return
		self.gateInfo[ playerBDID ] = boardPos
		for player in self.playerEntities:
			if boardPos == 0:
				player.client.onMoveRoleChessToStart( playerBDID )
				continue
			player.client.onMoveRoleChess( playerBDID, boardPos[0] )

	def onRolePassedGate( self, playerMB, playerBDID ):
		"""
		玩家完成某一个关卡
		"""
		if playerMB.id not in [ mb.id for mb in self.playerEntities ]:
			return
		
		self.gateInfo[ playerBDID ][ 1 ] = 1
	
	def rolePassedAllGate( self, playerMB, playerBDID ):
		"""
		通关处理
		"""
		self.removePlayer( playerMB )	 # 退出副本
		self.clearGateInfo( playerBDID )
		self.clearLivePointInfo( playerBDID )
		playerMB.cell.onPassedAllGate()

		if not self.winnerDBID:
			self.winnerDBID = playerBDID
			playerMB.client.desTrans_msgs( csdefine.DESTINY_TRANS_FIRST_NAME )
			# 给予奖励

	def roleReqOpenBoardInterface( self, playerMB ):
		"""
		玩家请求打开棋盘界面
		"""
		playerMB.cell.openBoardInterface( self.chessboardNo, self.gateInfo, self.livePointInfo )

	def onRoleDestroy( self, playerMB ):
		"""
		玩家下线
		"""
		self.removePlayer( playerMB )

	def removePlayer( self, playerMB ):
		"""
		移除玩家
		"""
		for index, mailbox in enumerate( self.playerEntities ):
			if mailbox.id == playerMB.id:
				self.playerEntities.pop( index )
				break
		if len( self.playerEntities ) == 0: # 副本里面人员全部离开
			self.closeDestinyTrans()

	def registerPlayer( self, playerMB ):
		"""
		添加玩家
		"""
		if playerMB.id not in [ mb.id for mb in self.playerEntities ]:
			self.playerEntities.append( playerMB )

	def clearGateInfo( self, dbid ):
		"""
		清除关卡信息
		"""
		if dbid in self.gateInfo.keys():
			self.gateInfo.pop( dbid  )

	def closeDestinyTrans( self ):
		"""
		关闭副本
		"""
		self.mgr.destroyDestinyTrans( self.uidKey, self.teamID )

	def onDestroy( self ):
		"""
		销毁
		"""
		# 通知玩家
		for player in self.playerEntities:
			player.cell.resetDestinyTransData()

	def onRoleLeaveTeam( self, playerMB, playerBDID ):
		"""
		玩家离队
		"""
		self.removePlayer( playerMB )
		self.clearGateInfo( playerBDID )
		self.clearLivePointInfo( playerBDID )
		playerMB.cell.dt_onLeaveTeamCB()

	def roleReEnter( self, playerMB, playerBDID ):
		"""
		玩家重新进入副本
		"""
		if playerBDID not in self.gateInfo.keys():
			playerMB.remoteCall( "statusMessage", ( csstatus.DESTINY_TRANS_IS_ON, ) )
			return
		
		self.registerPlayer( playerMB )
		playerMB.cell.reOpenBoardInterface( self.chessboardNo, self.gateInfo, self.livePointInfo, self.uidKey )

	def clearLivePointInfo( self, dbid ):
		"""
		清除玩家复活点数信息
		"""
		if dbid in self.livePointInfo.keys():
			self.livePointInfo.pop( dbid  )
		
		self.livePointInfoCheck()		# 复活点数信息有变化则需检测

	def roleLivePointChanged( self, playerMB, dbid, livePoint ):
		"""
		玩家复活点数发生变化
		"""
		if playerMB.id not in [ mb.id for mb in self.playerEntities ]:
			return
		self.livePointInfo[ dbid ] = livePoint
			
		for player in self.playerEntities:
			player.client.onRoleLivePointChanged( dbid, livePoint )

		self.livePointInfoCheck()

	def livePointInfoCheck( self ):
		"""
		玩家复活次数检测，如果所有玩家的复活次数均为负数，关闭副本
		"""
		for dbid in self.livePointInfo.keys():
			if self.livePointInfo[dbid] >= 0:
				return
		
		for player in self.playerEntities:
			player.client.desTrans_msgs( csdefine.DESTINY_TRANS_FAILED_GATE )
			player.cell.resetDestinyTransData()

		self.closeDestinyTrans()		# 关闭副本

class SpaceDestinyTransMgr( BigWorld.Base ):
	def __init__( self ):
		BigWorld.Base.__init__( self )
		self.registerGlobally( "SpaceDestinyTransMgr", self._onRegisterManager )
		self.destinyTransDict = {}				# 当前开启的天命轮回副本{ key:cItem ,}
		self.desTeamIDToKeys = {}				# { teamID:key }
		self.spaceInfo = {}						# 地图信息{type:{ spaceKey: enterPos, enterDir, } }
		self.initSpaceInfo()

	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register SpaceDestityTransMgr Fail!" )
			self.registerGlobally( "SpaceDestinyTransMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["SpaceDestinyTransMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("SpaceDestinyTransMgr Create Complete!")

	def initSpaceInfo( self ):
		"""
		初始化地图信息
		"""
		if BigWorld.globalData.has_key( "DestinyTransSpaceList" ):
			destinyTransSpaceList = BigWorld.globalData[ "DestinyTransSpaceList" ]
			for spaceInfo in destinyTransSpaceList:
				spaceKey = spaceInfo[0]
				bossID = spaceInfo[3]
			
				if bossID != "": 		# bossID 不为0即表示Boss关卡
					if GATE_TYPE_BOSS not in self.spaceInfo.keys():
						self.spaceInfo[ GATE_TYPE_BOSS ] = {}
					self.spaceInfo[ GATE_TYPE_BOSS ][ spaceKey ] = ( spaceInfo[1], spaceInfo[2] )
				else:
					if GATE_TYPE_COM not in self.spaceInfo.keys():
						self.spaceInfo[ GATE_TYPE_COM ] = {}
					self.spaceInfo[ GATE_TYPE_COM ][ spaceKey ] = ( spaceInfo[1], spaceInfo[2] )

			del BigWorld.globalData[ "DestinyTransSpaceList" ]

	def registerSpaceInfo( self, spaceKey, enterPos, enterDir, bossID ):
		"""
		define method
		注册地图信息
		"""
		if spaceKey in self.spaceInfo:
			ERROR_MSG( "Space key %s is alreay existed in SpaceDestinyTransMgr" % spaceKey )
			return
		if bossID != "": # bossID 不为0即表示Boss关卡
			if GATE_TYPE_BOSS not in self.spaceInfo.keys():
				self.spaceInfo[ GATE_TYPE_BOSS ] = {}
			self.spaceInfo[ GATE_TYPE_BOSS ][ spaceKey ] = ( enterPos, enterDir )
		else:
			if GATE_TYPE_COM not in self.spaceInfo.keys():
				self.spaceInfo[ GATE_TYPE_COM ] = {}
			self.spaceInfo[ GATE_TYPE_COM ][ spaceKey ] = ( enterPos, enterDir )

		self.spaceInfo[ spaceKey ] = ( enterPos, enterDir )

	def getDesItemByTeamID( self, teamID ):
		"""
		根据teamID找到对应的副本
		"""
		key = self.desTeamIDToKeys[ teamID ]
		cItem = self.destinyTransDict[ key ]
		return cItem

	def roleRequreEnter( self, playerMB, playerBDID, teamID, reqLevel ):
		"""
		define method
		玩家请求进入副本，先做条件检测
		若管理器中存在玩家的队伍ID，则做重新进入判断
		"""
		if teamID in self.desTeamIDToKeys.keys():
			cItem = self.getDesItemByTeamID( teamID )
			cItem.roleReEnter( playerMB, playerBDID )
			return
		playerMB.cell.roleEnterDestinyTransCheck( reqLevel )

	def onRequestDestinyTransCom( self,  playerEntities, dbidList, teamID ):
		"""
		define method
		申请进入天命轮回副本(普通模式)
		"""
		cItem = DestinyTransItemCom( self )
		cItem.playerEntities = playerEntities
		cItem.teamID = teamID
		# 初始化玩家关卡信息
		for dbid in dbidList:
			cItem.gateInfo[ dbid ] = [ 0, 0 ]
			cItem.livePointInfo[ dbid ] = csconst.DESTINY_TRANS_ROLE_INIT_LIVE_POINT
		
		# 选择棋盘
		cItem.chessboardNo = random.randint( 1, 3 )
		self.destinyTransDict[ cItem.getUIDKey() ] = cItem
		self.desTeamIDToKeys[ teamID ] = cItem.getUIDKey()
		cItem.start()

	def roleReqEnterDestinyGate( self, eventType, playerMB ):
		"""
		define method
		玩家请求进入关卡
		"""
		if eventType == csdefine.CHESS_BOARD_EVE_BOSS:		# Boss关卡
			spaceKey = random.sample( self.spaceInfo[ GATE_TYPE_BOSS ], 1 )[0]
			pos, dir = self.spaceInfo[ GATE_TYPE_BOSS ][ spaceKey ][0], self.spaceInfo[ GATE_TYPE_BOSS ][ spaceKey ][1]
		else:
			spaceKey = random.sample( self.spaceInfo[ GATE_TYPE_COM ], 1 )[0]
			pos, dir = self.spaceInfo[ GATE_TYPE_COM ][ spaceKey ][0], self.spaceInfo[ GATE_TYPE_COM ][ spaceKey ][1]
		
		playerMB.cell.gotoSpace( spaceKey, pos, dir )

	def updateRoleGateInfo( self, playerMB, playerBDID, teamID, boardPos ):
		"""
		define method
		更新玩家的位置信息
		"""
		cItem = self.getDesItemByTeamID( teamID )
		cItem.updateGateInfo( playerBDID, playerMB, boardPos )

	def roleReqOpenBoardInterface( self, playerMB, teamID ):
		"""
		define method
		玩家请求打开棋盘界面
		"""
		try:
			cItem = self.getDesItemByTeamID( teamID )
		except:
			return
		cItem.roleReqOpenBoardInterface( playerMB )

	def onRolePassedGate( self, playerMB, playerBDID, teamID ):
		"""
		define method
		有某一个副本的玩家完成关卡
		"""
		cItem = self.getDesItemByTeamID( teamID )
		cItem.onRolePassedGate( playerMB, playerBDID )

	def onRolePassedAllGate( self, playerMB, playerBDID, teamID ):
		"""
		define method
		玩家通关
		"""
		cItem = self.getDesItemByTeamID( teamID )
		cItem.rolePassedAllGate( playerMB, playerBDID )

	def onRoleDestroy( self, playerMB, destinyKey  ):
		"""
		define method 
		玩家下线
	 	"""
		cItem = self.destinyTransDict[ destinyKey ]
	 	cItem.onRoleDestroy( playerMB )

	def destroyDestinyTrans( self, destinyKey, teamID ):
		"""
		销毁副本
		"""
		if destinyKey in self.destinyTransDict.keys():
			cItem = self.destinyTransDict[ destinyKey ]
			cItem.onDestroy()
			self.destinyTransDict.pop( destinyKey )
		
		if teamID in self.desTeamIDToKeys.keys():
			self.desTeamIDToKeys.pop( teamID )

	def onRoleLeaveTeam( self, playerMB, playerBDID, destinyKey ):
		"""
		define method
		玩家离队
		"""
		if destinyKey in self.destinyTransDict:
			cItem = self.destinyTransDict[ destinyKey ]
			cItem.onRoleLeaveTeam( playerMB, playerBDID )

	def onRoleLivePointChanged( self, playerMB, playerBDID, teamID, livePoint ):
		"""
		define method
		玩家复活点数发生变化
		"""
		cItem = self.getDesItemByTeamID( teamID )
		cItem.roleLivePointChanged( playerMB, playerBDID, livePoint )