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

TELPORT_LOSER = 2222					# ��ֽ�����һ��ʱ�䣬��ʧ���ߴ�����ս��

class TeamWarItem:
	"""
	һ�����������
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
		self.realFightOrder = self.playerNames		# ʵʱ��ս˳��[ playerName1, plaeyrName2, playerName3 ]
		
	def update_fightPlayer( self, loseDBID ):
		"""
		���õ�ǰ��ս��
		"""
		if loseDBID not in self.fightPlayer:
			return
		self.fightPlayer.remove( loseDBID )
		dbid = self.getNextFightPlayer()
		if dbid:
			self.fightPlayer.append( dbid )
		
	def update_fightedPlayerDBID( self, loseDBID ):
		"""
		�����Ѷ�ս��¼
		"""
		if loseDBID not in self.fightedPlayerDBID:
			self.fightedPlayerDBID.append( loseDBID )
		self.updateRealFightOrder()											# ��ս����ı�
		for e in self.spaceEntity._players.values():
			e.client.campTurnWar_onPlayerLose( self.teamID, self.getPlayerName( loseDBID ) )		# ���ֱ��
			
	def isAllPlayerFighted( self ):
		"""
		ȫ����Ա��ս���
		"""
		return len( self.fightedPlayerDBID ) >= csconst.CAMP_TURN_MEMBER_NUM
		
	def updateRealFightOrder( self ):
		"""
		���¶�ս����
		"""
		self.realFightOrder = []
		for dbid in self.playerDBIDs:
			if dbid not in self.fightedPlayerDBID:
				self.realFightOrder.append( self.getPlayerName( dbid ) )		# �ȼ�δս��
		for dbid in self.fightedPlayerDBID:
			self.realFightOrder.append( self.getPlayerName( dbid ) )			# �ټ���ս��
				
	def getNextFightPlayer( self ):
		"""
		�����һ����ս��ҵ�dbid
		"""
		for dbid in self.playerDBIDs:
			if dbid not in self.fightedPlayerDBID and dbid not in self.fightPlayer:
				return dbid
		return None
	
	def getPlayerName( self, dbid ):
		"""
		��ñ���ĳ�˵�����
		"""
		for mem in self.dict["orderedPlayer"]:
			if mem[0] == dbid:
				return mem[1]
		return ""
	
	def getPlayerOrder( self, dbid ):
		"""
		���ĳ�˵Ķ�ս˳��
		"""
		if dbid in self.playerDBIDs:
			return self.playerDBIDs.index( dbid ) + 1
		return 0

class SpaceCopyCampTurnWar( SpaceCopy ):
	"""
	��ᳵ��ս�ռ�
	"""
	def __init__(self):
		SpaceCopy.__init__( self )
		self.isOver = False
		self.leftTeamItem = TeamWarItem( self, self.params["team_left"] )
		self.rightTeamItem = TeamWarItem( self, self.params["team_right"] )
		
		self.loseBase = []						# ʧ�ܵ����{teamID: baseMailbox}
		
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
		���������ĶԾֽ���
		"""
		if self.isOver == True:
			return
		self.isOver = True
		self.cell.allWarOver()
		
		for e in self._players.values():
			e.client.campTurnWar_showPlayerOrder( self.leftTeamItem.playerNames, self.rightTeamItem.playerNames )		# �ָ���ս˳����ʾ
			e.client.onStatusMessage( csstatus.TONG_TURN_SPACE_WAR_OVER, "" )
			
		if not hasWinner:		# ƽ��
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
		�ʱ�����
		"""
		if self.isOver == True:
			return
		self.cell.onActivityOver()
		
	def resultOnActivityOver( self, loseTeamID = None, winTeamID = None ):
		"""
		define method
		�ʱ�����ʱcell�Ǳߴ����������������Ѫ���ж�ʤ����
		"""
		if len( self.leftTeamItem.fightedPlayerDBID ) < len( self.rightTeamItem.fightedPlayerDBID ):		# ���ս����ұ��Ҷ���˵����ӻ�ʤ
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
		�����������ս��(ʱ�䵽Ѫ�����߰�)
		"""
		self.loseBase.append( loseBase )			# ���ڴ���
		self.addTimer( 3, 0, TELPORT_LOSER )
		self.__onBringResult( loseDBID, winnerDBID )
	
	def onPlayerLeave( self, playerDBID ):
		"""
		define method
		����뿪�ˣ�����ֱ�ӻ�ʤ
		
		@param plaeyrDBID: ���DBID
		"""
		self.__onBringResult( playerDBID )
	
	def __onBringResult( self, loseDBID, winnerDBID = None ):
		"""
		�����ս�ܻ�����뿪������һ�ֵĽ��
		"""
		tempList = [ loseDBID ]
		tempList.extend( self.leftTeamItem.fightedPlayerDBID )
		tempList.extend( self.rightTeamItem.fightedPlayerDBID )
		self.cell.setTemp( "losedPlayer", tempList )		# ������¼�ѶԾֽ�������ҵ�DBID
		
		losePlayerName = ""
		winPlayerName = ""
		playerName = ""
		loseTeamID = 0
		index = 0
		hasNext = False		# ��û����һλ������
		
		if loseDBID in self.leftTeamItem.fightPlayer:		# ���ս��
			self.leftTeamItem.update_fightedPlayerDBID( loseDBID )
			
			loseTeamID = self.leftTeamItem.teamID
			winTeamID = self.rightTeamItem.teamID
			
			if self.leftTeamItem.isAllPlayerFighted():		# û�к󱸶�Ա�˾ͽ�����������
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
				
				# ���¶�ս�����Ϣ
				self.leftTeamItem.update_fightPlayer( loseDBID )
				tempTuple = ( self.leftTeamItem.fightPlayer, self.rightTeamItem.fightPlayer )
				self.cell.setTemp("currentFightPlayer", tempTuple )
				
		elif loseDBID in self.rightTeamItem.fightPlayer:		# �Ҷ�ս��
			self.rightTeamItem.update_fightedPlayerDBID( loseDBID )
			
			loseTeamID = self.rightTeamItem.teamID
			winTeamID = self.leftTeamItem.teamID
			
			if self.rightTeamItem.isAllPlayerFighted():		# û�к󱸶�Ա�˾ͽ�����������
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
					
				# ���¶�ս�����Ϣ
				self.rightTeamItem.update_fightPlayer( loseDBID )
				tempTuple = ( self.leftTeamItem.fightPlayer, self.rightTeamItem.fightPlayer )
				self.cell.setTemp("currentFightPlayer", tempTuple )
			
		for e in self._players.values():
			e.client.campTurnWar_showPlayerOrder( self.leftTeamItem.realFightOrder, self.rightTeamItem.realFightOrder )		# ���¶�ս˳����ʾ
			if hasNext:
				if winPlayerName != "":			# �����ܵ����
					e.client.onStatusMessage( csstatus.TONG_TURN_WAR_ON_WIN, str(( winPlayerName, losePlayerName, index, playerName, )) )
					e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.TONG_TURN_WAR_ON_WIN %( winPlayerName, losePlayerName, index, playerName ), [] )
				else:							# �����볡�����
					e.client.onStatusMessage( csstatus.TONG_TURN_WAR_CHANGE_PLAYER_NOTIFY, str(( index, playerName, )) )
					e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.TONG_TURN_WAR_CHANGE_PLAYER_NOTIFY %( index, playerName ), [] )
			
		INFO_MSG( "SpaceCopyTongTurnWar (id: %s) bring loser.playerDBID:(%s), teamID:(%s)"%( self.id, loseDBID, loseTeamID ) )
	
	def __telportLoser( self ):
		"""
		ʧ���ߴ���
		"""
		for base in self.loseBase:
			base.cell.changePosAndDir( Math.Vector3( self.getScript().loser_watchPoint ), Math.Vector3( self.getScript().centerPoint ) )	# ������ս��
			base.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )						# ǿ����ҽ����ƽģʽ
			base.cell.removeTemp( "campTurnWar_isFightPlayer" )									# Ϊ���Ƴ�ս��״̬�µ�buff( Buff_1117 )
		self.loseBase = []
	
	def __telportNextFighter( self, dbid, isLeft ):
		"""
		���������ߴ�����ս��
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
		��ҽ����˿ռ�
		@param baseMailbox: ���mailbox
		@type baseMailbox: mailbox
		@param params: ���onEnterʱ��һЩ�������
		@type params: py_dict
		"""
		SpaceCopy.onEnter( self, baseMailbox, params )
		baseMailbox.client.campTurnWar_showPlayerOrder( self.leftTeamItem.playerNames, self.rightTeamItem.playerNames )
	
	def closeSpace( self, deleteFromDB = True ):
		"""
		"""
		BigWorld.globalData["CampMgr"].turnWar_unRegisterSpaceBase( self, [ self.leftTeamItem.teamID, self.rightTeamItem.teamID ] )
		SpaceCopy.closeSpace( self, deleteFromDB )