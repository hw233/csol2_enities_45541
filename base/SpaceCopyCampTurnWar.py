# -*- coding: gb18030 -*-


import time
import Math
from SpaceCopy import SpaceCopy
from bwdebug import *
import cschannel_msgs
import Love3
import csdefine
import csconst
import csstatus
import BigWorld

TELPORT_LOSER = 2222					# 大局结束后一段时间，将失败者传到观战区

class TeamWarItem:
	"""
	一个队伍的数据
	"""
	def __init__( self, spaceEntity, dict ):
		self.spaceEntity = spaceEntity
		self.dict = dict
		self.fightedPlayerDBID = []
		self.teamID = self.dict["teamID"]
		self.captainName = self.dict["captainName"]
		self.playerDBIDs = [ mem[0] for mem in self.dict["orderedPlayer"] ]
		self.playerNames = [ mem[1] for mem in self.dict["orderedPlayer"] ]
		self.fightPlayer = []			# dbid
		for i in self.playerDBIDs:
			if len( self.fightPlayer ) < csconst.TONG_TURN_FIGHT_MEM_NUM:
				self.fightPlayer.append( i )
		self.realFightOrder = self.playerNames		# 实时对战顺序[ playerName1, plaeyrName2, playerName3 ]
		
	def update_fightPlayer( self, loseDBID ):
		"""
		设置当前对战者
		"""
		if loseDBID not in self.fightPlayer:
			return
		self.fightPlayer.remove( loseDBID )
		dbid = self.getNextFightPlayer()
		if dbid:
			self.fightPlayer.append( dbid )
		
	def update_fightedPlayerDBID( self, loseDBID ):
		"""
		更新已对战记录
		"""
		if loseDBID not in self.fightedPlayerDBID:
			self.fightedPlayerDBID.append( loseDBID )
		self.updateRealFightOrder()											# 对战排序改变
		for e in self.spaceEntity._players.values():
			e.client.campTurnWar_onPlayerLose( self.teamID, self.getPlayerName( loseDBID ) )		# 名字变灰
			
	def isAllPlayerFighted( self ):
		"""
		全部队员对战完毕
		"""
		return len( self.fightedPlayerDBID ) >= csconst.CAMP_TURN_MEMBER_NUM
		
	def updateRealFightOrder( self ):
		"""
		更新对战排序
		"""
		self.realFightOrder = []
		for dbid in self.playerDBIDs:
			if dbid not in self.fightedPlayerDBID:
				self.realFightOrder.append( self.getPlayerName( dbid ) )		# 先加未战的
		for dbid in self.fightedPlayerDBID:
			self.realFightOrder.append( self.getPlayerName( dbid ) )			# 再加已战的
				
	def getNextFightPlayer( self ):
		"""
		获得下一个对战玩家的dbid
		"""
		for dbid in self.playerDBIDs:
			if dbid not in self.fightedPlayerDBID and dbid not in self.fightPlayer:
				return dbid
		return None
	
	def getPlayerName( self, dbid ):
		"""
		获得本队某人的名字
		"""
		for mem in self.dict["orderedPlayer"]:
			if mem[0] == dbid:
				return mem[1]
		return ""
	
	def getPlayerOrder( self, dbid ):
		"""
		获得某人的对战顺序
		"""
		if dbid in self.playerDBIDs:
			return self.playerDBIDs.index( dbid ) + 1
		return 0

class SpaceCopyCampTurnWar( SpaceCopy ):
	"""
	帮会车轮战空间
	"""
	def __init__(self):
		SpaceCopy.__init__( self )
		self.isOver = False
		self.leftTeamItem = TeamWarItem( self, self.params["team_left"] )
		self.rightTeamItem = TeamWarItem( self, self.params["team_right"] )
		
		self.loseBase = []						# 失败的玩家{teamID: baseMailbox}
		
		BigWorld.globalData["CampMgr"].turnWar_registerSpaceBase( self, [ self.leftTeamItem.teamID, self.rightTeamItem.teamID ] )
		
	def onGetCell( self ):
		"""
		"""
		self.cell.setTemp("currentFightPlayer", ( self.leftTeamItem.fightPlayer, self.rightTeamItem.fightPlayer ) )
		self.cell.setTemp( "losedPlayer", [] )
		self.cell.setTemp( "teamIDs",( self.leftTeamItem.teamID, self.rightTeamItem.teamID ) )
		SpaceCopy.onGetCell( self )
		
	def allWarOver( self, loseTeamID, winTeamID, hasWinner ):
		"""
		define method
		整个副本的对局结束
		"""
		if self.isOver == True:
			return
		self.isOver = True
		self.cell.allWarOver()
		
		for e in self._players.values():
			e.client.campTurnWar_showPlayerOrder( self.leftTeamItem.playerNames, self.rightTeamItem.playerNames )		# 恢复对战顺序显示
			e.client.onStatusMessage( csstatus.TONG_TURN_SPACE_WAR_OVER, "" )
			
		if not hasWinner:		# 平局
			BigWorld.globalData["CampMgr"].turnWar_onOneSpaceWarOver( loseTeamID, winTeamID, False )
			return
			
		BigWorld.globalData["CampMgr"].turnWar_onOneSpaceWarOver( loseTeamID, winTeamID, True )
		if winTeamID == self.leftTeamItem.teamID:
			winCaptainName = self.leftTeamItem.captainName
		elif winTeamID == self.rightTeamItem.teamID:
			winCaptainName = self.rightTeamItem.captainName
		for e in self._players.values():
			e.client.campTurnWar_updatePointShow( winTeamID )
			e.client.onStatusMessage( csstatus.TONG_TURN_WAR_TEAM_WIN_NOTIFY, str(( winCaptainName ,)) )
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.TONG_TURN_WAR_TEAM_WIN_NOTIFY %( winCaptainName ), [] )
			
	def onActivityOver( self ):
		"""
		define method
		活动时间结束
		"""
		if self.isOver == True:
			return
		self.cell.onActivityOver()
		
	def resultOnActivityOver( self, loseTeamID = None, winTeamID = None ):
		"""
		define method
		活动时间结束时cell那边传来比赛结果（根据血量判断胜负）
		"""
		if len( self.leftTeamItem.fightedPlayerDBID ) < len( self.rightTeamItem.fightedPlayerDBID ):		# 左队战败玩家比右队少说明左队获胜
			self.allWarOver( self.rightTeamItem.teamID, self.leftTeamItem.teamID, True )
		elif len( self.leftTeamItem.fightedPlayerDBID  ) > len( self.rightTeamItem.fightedPlayerDBID ):
			self.allWarOver( self.leftTeamItem.teamID, self.rightTeamItem.teamID, True )
		else:
			if winTeamID and loseTeamID:
				self.allWarOver( loseTeamID, winTeamID, True )
			else:
				self.allWarOver( self.leftTeamItem.teamID, self.rightTeamItem.teamID, False )
		
	def onPlayerWin( self, loseDBID, loseTeamID, loseBase, winnerDBID ):
		"""
		define method
		玩家死亡或者战败(时间到血量少者败)
		"""
		self.loseBase.append( loseBase )			# 用于传送
		self.addTimer( 3, 0, TELPORT_LOSER )
		self.__onBringResult( loseDBID, winnerDBID )
	
	def onPlayerLeave( self, playerDBID ):
		"""
		define method
		玩家离开了，对手直接获胜
		
		@param plaeyrDBID: 玩家DBID
		"""
		self.__onBringResult( playerDBID )
	
	def __onBringResult( self, loseDBID, winnerDBID = None ):
		"""
		因玩家战败或玩家离开而产生一局的结果
		"""
		tempList = [ loseDBID ]
		tempList.extend( self.leftTeamItem.fightedPlayerDBID )
		tempList.extend( self.rightTeamItem.fightedPlayerDBID )
		self.cell.setTemp( "losedPlayer", tempList )		# 副本记录已对局结束的玩家的DBID
		
		losePlayerName = ""
		winPlayerName = ""
		playerName = ""
		loseTeamID = 0
		index = 0
		hasNext = False		# 有没有下一位参赛者
		
		if loseDBID in self.leftTeamItem.fightPlayer:		# 左队战败
			self.leftTeamItem.update_fightedPlayerDBID( loseDBID )
			
			loseTeamID = self.leftTeamItem.teamID
			winTeamID = self.rightTeamItem.teamID
			
			if self.leftTeamItem.isAllPlayerFighted():		# 没有后备队员了就结束整场比赛
				self.allWarOver( loseTeamID, winTeamID, True )
				return
			else:
				if self.leftTeamItem.getNextFightPlayer():
					hasNext = True
					losePlayerName = self.leftTeamItem.getPlayerName( loseDBID )
					winPlayerName = self.rightTeamItem.getPlayerName( winnerDBID )
					index = self.leftTeamItem.getPlayerOrder( self.leftTeamItem.getNextFightPlayer() )
					playerName = self.leftTeamItem.getPlayerName( self.leftTeamItem.getNextFightPlayer() )
				
					self.__telportNextFighter( self.leftTeamItem.getNextFightPlayer(), True )
				
				# 更新对战玩家信息
				self.leftTeamItem.update_fightPlayer( loseDBID )
				tempTuple = ( self.leftTeamItem.fightPlayer, self.rightTeamItem.fightPlayer )
				self.cell.setTemp("currentFightPlayer", tempTuple )
				
		elif loseDBID in self.rightTeamItem.fightPlayer:		# 右队战败
			self.rightTeamItem.update_fightedPlayerDBID( loseDBID )
			
			loseTeamID = self.rightTeamItem.teamID
			winTeamID = self.leftTeamItem.teamID
			
			if self.rightTeamItem.isAllPlayerFighted():		# 没有后备队员了就结束整场比赛
				self.allWarOver( loseTeamID, winTeamID, True )
				return
			else:
				if self.rightTeamItem.getNextFightPlayer():
					hasNext = True
					losePlayerName = self.rightTeamItem.getPlayerName( loseDBID )
					winPlayerName = self.leftTeamItem.getPlayerName( winnerDBID )
					index = self.rightTeamItem.getPlayerOrder( self.rightTeamItem.getNextFightPlayer() )
					playerName = self.rightTeamItem.getPlayerName( self.rightTeamItem.getNextFightPlayer() )
					
					self.__telportNextFighter( self.rightTeamItem.getNextFightPlayer(), False )
					
				# 更新对战玩家信息
				self.rightTeamItem.update_fightPlayer( loseDBID )
				tempTuple = ( self.leftTeamItem.fightPlayer, self.rightTeamItem.fightPlayer )
				self.cell.setTemp("currentFightPlayer", tempTuple )
			
		for e in self._players.values():
			e.client.campTurnWar_showPlayerOrder( self.leftTeamItem.realFightOrder, self.rightTeamItem.realFightOrder )		# 更新对战顺序显示
			if hasNext:
				if winPlayerName != "":			# 被击败的情况
					e.client.onStatusMessage( csstatus.TONG_TURN_WAR_ON_WIN, str(( winPlayerName, losePlayerName, index, playerName, )) )
					e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.TONG_TURN_WAR_ON_WIN %( winPlayerName, losePlayerName, index, playerName ), [] )
				else:							# 主动离场的情况
					e.client.onStatusMessage( csstatus.TONG_TURN_WAR_CHANGE_PLAYER_NOTIFY, str(( index, playerName, )) )
					e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.TONG_TURN_WAR_CHANGE_PLAYER_NOTIFY %( index, playerName ), [] )
			
		INFO_MSG( "SpaceCopyTongTurnWar (id: %s) bring loser.playerDBID:(%s), teamID:(%s)"%( self.id, loseDBID, loseTeamID ) )
	
	def __telportLoser( self ):
		"""
		失败者处理
		"""
		for base in self.loseBase:
			base.cell.changePosAndDir( Math.Vector3( self.getScript().loser_watchPoint ), Math.Vector3( self.getScript().centerPoint ) )	# 传到观战区
			base.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )						# 强制玩家进入和平模式
			base.cell.removeTemp( "campTurnWar_isFightPlayer" )									# 为了移除战斗状态下的buff( Buff_1117 )
		self.loseBase = []
	
	def __telportNextFighter( self, dbid, isLeft ):
		"""
		后续参赛者传到出战点
		"""
		if isLeft:
			self.cell.telportPlayer( dbid, Math.Vector3( self.getScript().left_fightPoint ) )
		else:
			self.cell.telportPlayer( dbid, Math.Vector3( self.getScript().right_fightPoint ) )
		
	def onTimer( self, id, userArg ):
		if TELPORT_LOSER == userArg:
			self.__telportLoser()
			return
		SpaceCopy.onTimer( self, id, userArg )
		
	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		玩家进入了空间
		@param baseMailbox: 玩家mailbox
		@type baseMailbox: mailbox
		@param params: 玩家onEnter时的一些额外参数
		@type params: py_dict
		"""
		SpaceCopy.onEnter( self, baseMailbox, params )
		baseMailbox.client.campTurnWar_showPlayerOrder( self.leftTeamItem.playerNames, self.rightTeamItem.playerNames )
	
	def closeSpace( self, deleteFromDB = True ):
		"""
		"""
		BigWorld.globalData["CampMgr"].turnWar_unRegisterSpaceBase( self, [ self.leftTeamItem.teamID, self.rightTeamItem.teamID ] )
		SpaceCopy.closeSpace( self, deleteFromDB )