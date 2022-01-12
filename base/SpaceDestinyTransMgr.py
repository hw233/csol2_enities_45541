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
	���������ֻظ���
	"""
	def __init__( self, mgr ):
		self.mgr = mgr
		self.type = 0
		self.destinyManager = mgr				# ������
		self.chessboardNo = 0					# ���̱��
		self.uidKey = str( uuid.uuid1() )

	def getUIDKey( self ):
		"""
		��ȡ����Ψһ��ʶ
		"""
		return self.uidKey

class DestinyTransItemCom( DestinyTransItem ):
	"""
	��ͨģʽ
	"""
	def __init__( self, mgr ):
		"""
		"""
		DestinyTransItem.__init__( self, mgr )
		self.type = csdefine.ACTIVITY_DENTITY_TRANS_COM
		self.gateInfo = {}						# { playerBDID:( gateNo, hasFinish ),playerBDID:( gateNo, hasFinish ), }
		self.winnerDBID = 0						# ��һ��ͨ�����
		self.playerEntities = []
		self.livePointInfo = {}
		self.teamID = 0

	def start( self ):
		"""
		��������
		"""
		for playerMB in self.playerEntities:
			playerMB.cell.destinyTransSpaceStart( self.chessboardNo, self.gateInfo, self.livePointInfo, self.uidKey )

	def updateGateInfo( self, playerBDID, playerMB, boardPos ):
		"""
		���½�ɫ����λ����Ϣ
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
		������ĳһ���ؿ�
		"""
		if playerMB.id not in [ mb.id for mb in self.playerEntities ]:
			return
		
		self.gateInfo[ playerBDID ][ 1 ] = 1
	
	def rolePassedAllGate( self, playerMB, playerBDID ):
		"""
		ͨ�ش���
		"""
		self.removePlayer( playerMB )	 # �˳�����
		self.clearGateInfo( playerBDID )
		self.clearLivePointInfo( playerBDID )
		playerMB.cell.onPassedAllGate()

		if not self.winnerDBID:
			self.winnerDBID = playerBDID
			playerMB.client.desTrans_msgs( csdefine.DESTINY_TRANS_FIRST_NAME )
			# ���轱��

	def roleReqOpenBoardInterface( self, playerMB ):
		"""
		�����������̽���
		"""
		playerMB.cell.openBoardInterface( self.chessboardNo, self.gateInfo, self.livePointInfo )

	def onRoleDestroy( self, playerMB ):
		"""
		�������
		"""
		self.removePlayer( playerMB )

	def removePlayer( self, playerMB ):
		"""
		�Ƴ����
		"""
		for index, mailbox in enumerate( self.playerEntities ):
			if mailbox.id == playerMB.id:
				self.playerEntities.pop( index )
				break
		if len( self.playerEntities ) == 0: # ����������Աȫ���뿪
			self.closeDestinyTrans()

	def registerPlayer( self, playerMB ):
		"""
		������
		"""
		if playerMB.id not in [ mb.id for mb in self.playerEntities ]:
			self.playerEntities.append( playerMB )

	def clearGateInfo( self, dbid ):
		"""
		����ؿ���Ϣ
		"""
		if dbid in self.gateInfo.keys():
			self.gateInfo.pop( dbid  )

	def closeDestinyTrans( self ):
		"""
		�رո���
		"""
		self.mgr.destroyDestinyTrans( self.uidKey, self.teamID )

	def onDestroy( self ):
		"""
		����
		"""
		# ֪ͨ���
		for player in self.playerEntities:
			player.cell.resetDestinyTransData()

	def onRoleLeaveTeam( self, playerMB, playerBDID ):
		"""
		������
		"""
		self.removePlayer( playerMB )
		self.clearGateInfo( playerBDID )
		self.clearLivePointInfo( playerBDID )
		playerMB.cell.dt_onLeaveTeamCB()

	def roleReEnter( self, playerMB, playerBDID ):
		"""
		������½��븱��
		"""
		if playerBDID not in self.gateInfo.keys():
			playerMB.remoteCall( "statusMessage", ( csstatus.DESTINY_TRANS_IS_ON, ) )
			return
		
		self.registerPlayer( playerMB )
		playerMB.cell.reOpenBoardInterface( self.chessboardNo, self.gateInfo, self.livePointInfo, self.uidKey )

	def clearLivePointInfo( self, dbid ):
		"""
		�����Ҹ��������Ϣ
		"""
		if dbid in self.livePointInfo.keys():
			self.livePointInfo.pop( dbid  )
		
		self.livePointInfoCheck()		# ���������Ϣ�б仯������

	def roleLivePointChanged( self, playerMB, dbid, livePoint ):
		"""
		��Ҹ�����������仯
		"""
		if playerMB.id not in [ mb.id for mb in self.playerEntities ]:
			return
		self.livePointInfo[ dbid ] = livePoint
			
		for player in self.playerEntities:
			player.client.onRoleLivePointChanged( dbid, livePoint )

		self.livePointInfoCheck()

	def livePointInfoCheck( self ):
		"""
		��Ҹ��������⣬���������ҵĸ��������Ϊ�������رո���
		"""
		for dbid in self.livePointInfo.keys():
			if self.livePointInfo[dbid] >= 0:
				return
		
		for player in self.playerEntities:
			player.client.desTrans_msgs( csdefine.DESTINY_TRANS_FAILED_GATE )
			player.cell.resetDestinyTransData()

		self.closeDestinyTrans()		# �رո���

class SpaceDestinyTransMgr( BigWorld.Base ):
	def __init__( self ):
		BigWorld.Base.__init__( self )
		self.registerGlobally( "SpaceDestinyTransMgr", self._onRegisterManager )
		self.destinyTransDict = {}				# ��ǰ�����������ֻظ���{ key:cItem ,}
		self.desTeamIDToKeys = {}				# { teamID:key }
		self.spaceInfo = {}						# ��ͼ��Ϣ{type:{ spaceKey: enterPos, enterDir, } }
		self.initSpaceInfo()

	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register SpaceDestityTransMgr Fail!" )
			self.registerGlobally( "SpaceDestinyTransMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["SpaceDestinyTransMgr"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("SpaceDestinyTransMgr Create Complete!")

	def initSpaceInfo( self ):
		"""
		��ʼ����ͼ��Ϣ
		"""
		if BigWorld.globalData.has_key( "DestinyTransSpaceList" ):
			destinyTransSpaceList = BigWorld.globalData[ "DestinyTransSpaceList" ]
			for spaceInfo in destinyTransSpaceList:
				spaceKey = spaceInfo[0]
				bossID = spaceInfo[3]
			
				if bossID != "": 		# bossID ��Ϊ0����ʾBoss�ؿ�
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
		ע���ͼ��Ϣ
		"""
		if spaceKey in self.spaceInfo:
			ERROR_MSG( "Space key %s is alreay existed in SpaceDestinyTransMgr" % spaceKey )
			return
		if bossID != "": # bossID ��Ϊ0����ʾBoss�ؿ�
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
		����teamID�ҵ���Ӧ�ĸ���
		"""
		key = self.desTeamIDToKeys[ teamID ]
		cItem = self.destinyTransDict[ key ]
		return cItem

	def roleRequreEnter( self, playerMB, playerBDID, teamID, reqLevel ):
		"""
		define method
		���������븱���������������
		���������д�����ҵĶ���ID���������½����ж�
		"""
		if teamID in self.desTeamIDToKeys.keys():
			cItem = self.getDesItemByTeamID( teamID )
			cItem.roleReEnter( playerMB, playerBDID )
			return
		playerMB.cell.roleEnterDestinyTransCheck( reqLevel )

	def onRequestDestinyTransCom( self,  playerEntities, dbidList, teamID ):
		"""
		define method
		������������ֻظ���(��ͨģʽ)
		"""
		cItem = DestinyTransItemCom( self )
		cItem.playerEntities = playerEntities
		cItem.teamID = teamID
		# ��ʼ����ҹؿ���Ϣ
		for dbid in dbidList:
			cItem.gateInfo[ dbid ] = [ 0, 0 ]
			cItem.livePointInfo[ dbid ] = csconst.DESTINY_TRANS_ROLE_INIT_LIVE_POINT
		
		# ѡ������
		cItem.chessboardNo = random.randint( 1, 3 )
		self.destinyTransDict[ cItem.getUIDKey() ] = cItem
		self.desTeamIDToKeys[ teamID ] = cItem.getUIDKey()
		cItem.start()

	def roleReqEnterDestinyGate( self, eventType, playerMB ):
		"""
		define method
		����������ؿ�
		"""
		if eventType == csdefine.CHESS_BOARD_EVE_BOSS:		# Boss�ؿ�
			spaceKey = random.sample( self.spaceInfo[ GATE_TYPE_BOSS ], 1 )[0]
			pos, dir = self.spaceInfo[ GATE_TYPE_BOSS ][ spaceKey ][0], self.spaceInfo[ GATE_TYPE_BOSS ][ spaceKey ][1]
		else:
			spaceKey = random.sample( self.spaceInfo[ GATE_TYPE_COM ], 1 )[0]
			pos, dir = self.spaceInfo[ GATE_TYPE_COM ][ spaceKey ][0], self.spaceInfo[ GATE_TYPE_COM ][ spaceKey ][1]
		
		playerMB.cell.gotoSpace( spaceKey, pos, dir )

	def updateRoleGateInfo( self, playerMB, playerBDID, teamID, boardPos ):
		"""
		define method
		������ҵ�λ����Ϣ
		"""
		cItem = self.getDesItemByTeamID( teamID )
		cItem.updateGateInfo( playerBDID, playerMB, boardPos )

	def roleReqOpenBoardInterface( self, playerMB, teamID ):
		"""
		define method
		�����������̽���
		"""
		try:
			cItem = self.getDesItemByTeamID( teamID )
		except:
			return
		cItem.roleReqOpenBoardInterface( playerMB )

	def onRolePassedGate( self, playerMB, playerBDID, teamID ):
		"""
		define method
		��ĳһ�������������ɹؿ�
		"""
		cItem = self.getDesItemByTeamID( teamID )
		cItem.onRolePassedGate( playerMB, playerBDID )

	def onRolePassedAllGate( self, playerMB, playerBDID, teamID ):
		"""
		define method
		���ͨ��
		"""
		cItem = self.getDesItemByTeamID( teamID )
		cItem.rolePassedAllGate( playerMB, playerBDID )

	def onRoleDestroy( self, playerMB, destinyKey  ):
		"""
		define method 
		�������
	 	"""
		cItem = self.destinyTransDict[ destinyKey ]
	 	cItem.onRoleDestroy( playerMB )

	def destroyDestinyTrans( self, destinyKey, teamID ):
		"""
		���ٸ���
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
		������
		"""
		if destinyKey in self.destinyTransDict:
			cItem = self.destinyTransDict[ destinyKey ]
			cItem.onRoleLeaveTeam( playerMB, playerBDID )

	def onRoleLivePointChanged( self, playerMB, playerBDID, teamID, livePoint ):
		"""
		define method
		��Ҹ�����������仯
		"""
		cItem = self.getDesItemByTeamID( teamID )
		cItem.roleLivePointChanged( playerMB, playerBDID, livePoint )