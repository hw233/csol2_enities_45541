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

START_NEXT_WAR = 11111			# ��һ�ʤ���һ��ʱ���ٴ���
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
		self.fightPlayer = self.playerDBIDs[0]		# dbid
		self.realFightOrder = self.playerNames		# ʵʱ��ս˳��[ playerName1, plaeyrName2, playerName3 ]
		
	def update_fightPlayer( self ):
		"""
		���õ�ǰ��ս��
		"""
		dbid = self.getNextFightPlayer()
		if dbid:
			self.fightPlayer = dbid
		
	def update_fightedPlayerDBID( self ):
		"""
		�����Ѷ�ս��¼
		"""
		if self.fightPlayer not in self.fightedPlayerDBID:
			self.fightedPlayerDBID.append( self.fightPlayer )
		self.updateRealFightOrder()											# ��ս����ı�
		for e in self.spaceEntity._players.values():
			e.client.turnWar_onPlayerLose( self.teamID, self.getPlayerName( self.fightPlayer ) )		# ���ֱ��
			
	def isAllPlayerFighted( self ):
		"""
		ȫ����Ա��ս���
		"""
		return len( self.fightedPlayerDBID ) >= csconst.TONG_TURN_MEMBER_NUM
		
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
			if dbid not in self.fightedPlayerDBID:
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

class SpaceCopyTongTurnWar( SpaceCopy ):
	"""
	��ᳵ��ս�ռ�
	"""
	def __init__(self):
		SpaceCopy.__init__( self )
		self.isOver = False
		self.leftTeamItem = TeamWarItem( self, self.params["team_left"] )
		self.rightTeamItem = TeamWarItem( self, self.params["team_right"] )
		
		self.loseBase = []						# ʧ�ܵ����{teamID: baseMailbox}
		
		BigWorld.globalData["TongManager"].registerSpaceBase( self, [ self.leftTeamItem.teamID, self.rightTeamItem.teamID ] )
		
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
			e.client.turnWar_showPlayerOrder( self.leftTeamItem.playerNames, self.rightTeamItem.playerNames )		# �ָ���ս˳����ʾ
			e.client.onStatusMessage( csstatus.TONG_TURN_SPACE_WAR_OVER, "" )
			
		if not hasWinner:		# ƽ��
			BigWorld.globalData["TongManager"].onOneSpaceWarOver( loseTeamID, winTeamID, False )
			return
			
		BigWorld.globalData["TongManager"].onOneSpaceWarOver( loseTeamID, winTeamID, True )
		if winTeamID == self.leftTeamItem.teamID:
			winCaptainName = self.leftTeamItem.captainName
		elif winTeamID == self.rightTeamItem.teamID:
			winCaptainName = self.rightTeamItem.captainName
		for e in self._players.values():
			e.client.turnWar_updatePointShow( winTeamID )
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
		
	def onPlayerWin( self, loseDBID, loseTeamID, loseBase ):
		"""
		define method
		�����������ս��(ʱ�䵽Ѫ�����߰�)
		"""
		self.loseBase.append( loseBase )			# �����¾ֿ�ʼʱ�Ĵ���
		self.addTimer( 3, 0, TELPORT_LOSER )
		self.__onBringResult( loseDBID )
	
	def onPlayerLeave( self, playerDBID ):
		"""
		define method
		����뿪�ˣ�����ֱ�ӻ�ʤ
		
		@param plaeyrDBID: ���DBID
		"""
		self.__onBringResult( playerDBID )
		
	def onBothPlayerLoseOrLeave( self, isDogfall, loseBases = [] ):
		"""
		define method
		ƽ�ֻ��߶��뿪�����
		@param isDogfall: TrueΪƽ�ֵ����������Ϊ���볡�����
		"""
		self.leftTeamItem.update_fightedPlayerDBID()
		self.rightTeamItem.update_fightedPlayerDBID()
		
		tempList = []
		tempList.extend( self.leftTeamItem.fightedPlayerDBID )
		tempList.extend( self.rightTeamItem.fightedPlayerDBID )
		self.cell.setTemp( "losedPlayer", tempList )
		
		if isDogfall:
			self.loseBase.extend( loseBases )
			self.addTimer( 3, 0, TELPORT_LOSER )
		
		if self.leftTeamItem.isAllPlayerFighted() and self.rightTeamItem.isAllPlayerFighted():
			self.allWarOver( self.leftTeamItem.teamID, self.rightTeamItem.teamID, False )
		elif self.leftTeamItem.isAllPlayerFighted():
			self.allWarOver( self.leftTeamItem.teamID, self.rightTeamItem.teamID, True )
		elif self.rightTeamItem.isAllPlayerFighted():
			self.allWarOver( self.rightTeamItem.teamID, self.leftTeamItem.teamID, True )
		
		else:			# ��Ҫ������ȥ
			self.leftTeamItem.update_fightPlayer()
			self.rightTeamItem.update_fightPlayer()
			tempTuple = ( self.leftTeamItem.fightPlayer, self.rightTeamItem.fightPlayer )
			self.cell.setTemp("currentFightPlayer", tempTuple )
			
			leftIndex = self.leftTeamItem.getPlayerOrder( self.leftTeamItem.fightPlayer )
			leftPlayerName = self.leftTeamItem.getPlayerName( self.leftTeamItem.fightPlayer )
			
			rightIndex = self.rightTeamItem.getPlayerOrder( self.rightTeamItem.fightPlayer )
			rightPlayerName = self.rightTeamItem.getPlayerName( self.rightTeamItem.fightPlayer )
			
			for e in self._players.values():
				e.client.turnWar_showPlayerOrder( self.leftTeamItem.realFightOrder, self.rightTeamItem.realFightOrder )		# ���¶�ս˳����ʾ
				e.client.onStatusMessage( csstatus.TONG_TURN_WAR_CHANGE_PLAYER_NOTIFY, str(( leftIndex, leftPlayerName, )) )
				e.client.onStatusMessage( csstatus.TONG_TURN_WAR_CHANGE_PLAYER_NOTIFY, str(( rightIndex, rightPlayerName, )) )
				e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.TONG_TURN_WAR_CHANGE_PLAYER_NOTIFY %( leftIndex, leftPlayerName ), [] )
				e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.TONG_TURN_WAR_CHANGE_PLAYER_NOTIFY %( rightIndex, rightPlayerName ), [] )
			
			self.addTimer( 5, 0, START_NEXT_WAR )			# 5���Ӻ�ʼ��һ��
		
		INFO_MSG( "SpaceCopyTongTurnWar both player leave or is dogfall. space id: %s" % self.id )
			
	def __onBringResult( self, loseDBID ):
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
		if loseDBID == self.leftTeamItem.fightPlayer:		# ���ս��
			self.leftTeamItem.update_fightedPlayerDBID()
			
			loseTeamID = self.leftTeamItem.teamID
			winTeamID = self.rightTeamItem.teamID
			losePlayerName = self.leftTeamItem.getPlayerName( loseDBID )
			winPlayerName = self.rightTeamItem.getPlayerName( self.rightTeamItem.fightPlayer )
			
			if self.leftTeamItem.isAllPlayerFighted():		# û�к󱸶�Ա�˾ͽ���������
				self.allWarOver( loseTeamID, winTeamID, True )
				return
			else:
				# ���¶�ս�����Ϣ
				self.leftTeamItem.update_fightPlayer()
				tempTuple = ( self.leftTeamItem.fightPlayer, self.rightTeamItem.fightPlayer )
				self.cell.setTemp("currentFightPlayer", tempTuple )
				
				index = self.leftTeamItem.getPlayerOrder( self.leftTeamItem.fightPlayer )
				playerName = self.leftTeamItem.getPlayerName( self.leftTeamItem.fightPlayer )
				
		elif loseDBID == self.rightTeamItem.fightPlayer:		# �Ҷ�ս��
			self.rightTeamItem.update_fightedPlayerDBID()
			
			loseTeamID = self.rightTeamItem.teamID
			winTeamID = self.leftTeamItem.teamID
			losePlayerName = self.rightTeamItem.getPlayerName( loseDBID )
			winPlayerName = self.leftTeamItem.getPlayerName( self.leftTeamItem.fightPlayer )
			
			if self.rightTeamItem.isAllPlayerFighted():		# û�к󱸶�Ա�˾ͽ���������
				self.allWarOver( loseTeamID, winTeamID, True )
				return
			else:
				# ���¶�ս�����Ϣ
				self.rightTeamItem.update_fightPlayer()
				tempTuple = ( self.leftTeamItem.fightPlayer, self.rightTeamItem.fightPlayer )
				self.cell.setTemp("currentFightPlayer", tempTuple )
			
			index = self.rightTeamItem.getPlayerOrder( self.rightTeamItem.fightPlayer )
			playerName = self.rightTeamItem.getPlayerName( self.rightTeamItem.fightPlayer )
		
		for e in self._players.values():
			e.client.turnWar_showPlayerOrder( self.leftTeamItem.realFightOrder, self.rightTeamItem.realFightOrder )		# ���¶�ս˳����ʾ
			e.client.onStatusMessage( csstatus.TONG_TURN_WAR_ON_WIN, str(( winPlayerName, losePlayerName, index, playerName, )) )
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.TONG_TURN_WAR_ON_WIN %( winPlayerName, losePlayerName, index, playerName ), [] )
		
		self.addTimer( 5, 0, START_NEXT_WAR )			# 5���Ӻ�ʼ��һ��
		INFO_MSG( "SpaceCopyTongTurnWar bring loser.playerDBID:(%s), teamID:(%s)"%( loseDBID, loseTeamID ) )
	
	def startNextWar( self ):
		# ������һ�ֶ�ս
		self.cell.startNextWar()
	
	def __telportLoser( self ):
		"""
		ʧ���ߴ���
		"""
		for base in self.loseBase:
			base.cell.changePosition( Math.Vector3( self.getScript().loser_watchPoint ) )	# ������ս��
			base.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )						# ǿ����ҽ����ƽģʽ
			base.cell.removeTemp( "turnWar_isFightPlayer" )									# Ϊ���Ƴ�ս��״̬�µ�buff( Buff_299039 )
		self.loseBase = []
		
	def onTimer( self, id, userArg ):
		if START_NEXT_WAR == userArg:
			self.startNextWar()
			return
		elif TELPORT_LOSER == userArg:
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
		baseMailbox.client.turnWar_showPlayerOrder( self.leftTeamItem.playerNames, self.rightTeamItem.playerNames )
	
	def closeSpace( self, deleteFromDB = True ):
		"""
		"""
		BigWorld.globalData["TongManager"].unRegisterSpaceBase( self, [ self.leftTeamItem.teamID, self.rightTeamItem.teamID ] )
		SpaceCopy.closeSpace( self, deleteFromDB )